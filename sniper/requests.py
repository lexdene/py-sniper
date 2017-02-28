import urllib.parse
from collections import namedtuple
from http.cookies import SimpleCookie

from .utils import QueryList

Url = namedtuple(
    'Url',
    ['scheme', 'host', 'path', 'query'],
)


class Request:
    def __init__(self, app, method, uri, headers=None, body=None):
        self.app = app
        self.method = method
        self.raw_uri = uri
        self.headers = QueryList(headers or [])
        self.body = body or ''

        # url
        parse_result = urllib.parse.urlparse(uri)
        host = self.headers.get('Host', parse_result.netloc)

        self.url = Url(
            scheme=parse_result.scheme,
            host=host,
            path=parse_result.path,
            query=QueryList(urllib.parse.parse_qsl(parse_result.query)),
        )

        cookie_header = self.headers.get('Cookie')
        self.cookie = dict(
            (key, c.value)
            for key, c in SimpleCookie(cookie_header).items()
        )

    @property
    def query(self):
        return self.url.query
