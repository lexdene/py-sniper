import unittest
from asyncio import iscoroutinefunction
from functools import wraps
from http.cookies import SimpleCookie
from urllib.parse import urlencode

from .app import BaseApp
from .requests import Request


class TestClient:
    def __init__(self, app):
        self.app = app
        self.cookies = None

    def set_cookie(self, key, value):
        if self.cookies is None:
            self.cookies = SimpleCookie()

        self.cookies[key] = value

    async def request(self, method, path,
                      query=None, body=None, headers=None,
                      data=None):
        headers = headers or []

        if body is None:
            if data:
                body = urlencode(data)
                headers.append(
                    ('Content-Type', 'application/x-www-form-urlencoded')
                )

        if self.cookies:
            cookie_header = '; '.join(
                v.OutputString()
                for v in self.cookies.values()
            )
            headers.append(
                ('Cookie', cookie_header)
            )

        if body and isinstance(body, str):
            body = body.encode('utf-8')

        request = Request(
            app=self.app,
            reader=None,
            method=method.upper(),
            uri=path,
            headers=headers,
            body=body,
        )
        response = await self.app.process_request(request)
        if response.cookies:
            self.cookies = response.cookies

        return response

    def __getattr__(self, name):

        def _request(*argv, **kwargs):
            return self.request(name, *argv, **kwargs)

        return _request


class TestApp(BaseApp):
    pass


class WrapCoroutines(type):
    def __new__(cls, name, bases, classdict):
        for key, value in classdict.items():
            if key.startswith('test') and iscoroutinefunction(value):
                classdict[key] = _run_coroutine(value)

        return type.__new__(cls, name, bases, classdict)


class TestCase(unittest.TestCase, metaclass=WrapCoroutines):
    pass


def _run_coroutine(func):

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        future = func(self, *args, **kwargs)
        self.app.loop.run_until_complete(future)
    return wrapper
