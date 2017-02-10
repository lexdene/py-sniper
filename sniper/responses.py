from http import HTTPStatus

from .headers import Header
from .parsers import RawHttpResponse


class BaseResponse:
    def __init__(self, body, header, status_code, status_phrase):
        assert isinstance(header, Header), 'header must be a Header object'

        self.body = body
        self.header = header
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
        self.body = body
        self.header = Header(headers or [])

        self.status_code = status_code

        if status_phrase is None:
            status_phrase = HTTPStatus(status_code).phrase
        self.status_phrase = status_phrase
