import asyncio
import unittest
from functools import wraps

from .app import BaseApp
from .parsers import RawHttpRequest


class TestClient:
    def __init__(self, app):
        self.app = app

    async def request(self, method, path, query=None, body=None, headers=None):
        request = RawHttpRequest(
            method=method,
            uri=path,
            http_version='1.1',
            headers=headers or [],
            body=body or '',
        )
        response = await self.app.process_request(request)
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
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper
