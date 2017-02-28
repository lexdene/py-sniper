from http import HTTPStatus
from http.cookies import SimpleCookie

from .utils import QueryList


class BaseResponse:
    def __init__(self, body, headers,
                 status_code, status_phrase, cookies=None):
        assert isinstance(headers, QueryList), (
            'header must be a QueryList object'
        )

        self.body = body
        self.headers = headers
        self.status_code = status_code
        self.status_phrase = status_phrase

        self.cookies = SimpleCookie(cookies)

    def freeze_headers(self):
        headers = [
            ('Content-Length', len(self.body)),
        ]
        for key, value in self.headers.items():
            headers.append((key, value))

        for v in self.cookies.values():
            headers.append(('Set-Cookie', v.OutputString()))

        return QueryList(headers)


class Response(BaseResponse):
    def __init__(self, body, headers=None,
                 status_code=200, status_phrase=None, cookies=None):
        headers = QueryList(headers or [])

        if status_phrase is None:
            status_phrase = HTTPStatus(status_code).phrase

        super().__init__(body, headers, status_code, status_phrase, cookies)
