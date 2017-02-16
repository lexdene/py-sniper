from http import HTTPStatus

from .headers import Header
from .parsers import RawHttpResponse


class BaseResponse:
    def __init__(self, body, headers, status_code, status_phrase):
        assert isinstance(headers, Header), 'header must be a Header object'

        self.body = body
        self.headers = headers
        self.status_code = status_code
        self.status_phrase = status_phrase

    def build_raw_response(self):
        return RawHttpResponse(
            http_version='1.1',
            status_code=self.status_code,
            reason_phrase=self.status_phrase,
            headers=[
                ('Content-Length', len(self.body)),
            ],
            body=self.body,
        )


class Response(BaseResponse):
    def __init__(self, body, headers=None,
                 status_code=200, status_phrase=None):
        headers = Header(headers or [])

        if status_phrase is None:
            status_phrase = HTTPStatus(status_code).phrase

        super().__init__(body, headers, status_code, status_phrase)
