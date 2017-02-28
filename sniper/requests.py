import urllib.parse
from collections import namedtuple
from http.cookies import SimpleCookie

from .utils import QueryList


Url = namedtuple(
    'Url',
    ['scheme', 'host', 'path', 'query'],
)


class Request:
    def __init__(self, app, method, url, headers, body):
        self.app = app
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body

        cookie_header = self.headers.get('Cookie')
        self.cookie = dict(
            (key, c.value)
            for key, c in SimpleCookie(cookie_header).items()
        )

    @property
    def query(self):
        return self.url.query

    @classmethod
    def build_from_raw_request(cls, raw_request, app):
        headers = QueryList(raw_request.headers)

        # url
        parse_result = urllib.parse.urlparse(raw_request.uri)

        host = headers.get('Host', parse_result.netloc)

        url = Url(
            scheme=parse_result.scheme,
            host=host,
            path=parse_result.path,
            query=QueryList(urllib.parse.parse_qsl(parse_result.query)),
        )

        return cls(
            app=app,
            method=raw_request.method.upper(),
            url=url,
            headers=headers,
            body=raw_request.body,
        )
