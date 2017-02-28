from http import HTTPStatus
from http.cookies import SimpleCookie

from .headers import Header
from .parsers import RawHttpResponse


class BaseResponse:
    def __init__(self, body, headers,
                 status_code, status_phrase, cookies=None):
        assert isinstance(headers, Header), 'header must be a Header object'

        self.body = body
        self.headers = headers
        self.status_code = status_code
        self.status_phrase = status_phrase

        self.cookies = SimpleCookie(cookies)

    def build_raw_response(self):
        headers = [
            ('Content-Length', len(self.body)),
        ]
        for key, value in self.headers.items():
            headers.append((key, value))

        for v in self.cookies.values():
            headers.append(('Set-Cookie', v.OutputString()))

        return RawHttpResponse(
            http_version='1.1',
            status_code=self.status_code,
            reason_phrase=self.status_phrase,
            body=self.body,
            headers=headers,
        )


class Response(BaseResponse):
    def __init__(self, body, headers=None,
                 status_code=200, status_phrase=None, cookies=None):
        headers = Header(headers or [])

        if status_phrase is None:
            status_phrase = HTTPStatus(status_code).phrase

        super().__init__(body, headers, status_code, status_phrase, cookies)
