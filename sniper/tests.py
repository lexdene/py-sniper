import unittest
from functools import wraps
from urllib.parse import urlencode

from .app import BaseApp
from .requests import Request


class TestClient:
    def __init__(self, app):
        self.app = app
        self.cookies = None

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

        request = Request(
            app=self.app,
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


class TestCase(unittest.TestCase):
    pass


def run_coroutine(f):

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        future = f(self, *args, **kwargs)
        self.app.loop.run_until_complete(future)
    return wrapper
