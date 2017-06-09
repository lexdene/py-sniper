from http import HTTPStatus
from http.cookies import SimpleCookie

from .utils import QueryList, is_async_generator

DEFAULT_CONTENT_TYPE = 'text/plain'
DEFAULT_CHARSET = 'utf-8'


class BaseResponse:
    def __init__(self, body, headers,
                 status_code, status_phrase, cookies=None,
                 content_type=None, charset=None):
        assert is_async_generator(body) or isinstance(body, (str, bytes)), (
            'body must be str or bytes or async generator, got: %s' % (
                type(body),
            )
        )
        assert isinstance(headers, QueryList), (
            'header must be a QueryList object'
        )
        assert isinstance(status_code, int)
        assert isinstance(status_phrase, str)

        self.body = body
        self.headers = headers
        self.status_code = status_code
        self.status_phrase = status_phrase
        self.content_type = content_type or DEFAULT_CONTENT_TYPE
        self.charset = charset or DEFAULT_CHARSET

        self.cookies = SimpleCookie(cookies)

    def freeze_headers(self):
        headers = []

        contains_content_type = False
        for key, value in self.headers.items():
            headers.append((key, value))

            if key == 'Content-Type':
                contains_content_type = True

        if not contains_content_type:
            headers.append((
                'Content-Type',
                '%s; charset=%s' % (self.content_type, self.charset)
            ))

        for v in self.cookies.values():
            headers.append(('Set-Cookie', v.OutputString()))

        return QueryList(headers)


class Response(BaseResponse):
    def __init__(self, body='', headers=None,
                 status_code=200, status_phrase=None, cookies=None,
                 **kwargs):
        headers = QueryList(headers or [])

        if status_phrase is None:
            status_phrase = HTTPStatus(status_code).phrase

        super().__init__(
            body, headers,
            status_code, status_phrase,
            cookies, **kwargs
        )
