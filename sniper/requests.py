import cgi
import json
import urllib.parse
from collections import namedtuple
from http.cookies import SimpleCookie
from io import BytesIO

from .utils import QueryList, cached_property

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

    @cached_property
    def data(self):
        content_type = self.headers.get('Content-Type')
        parts = content_type.split(';')
        media_type = parts.pop(0)

        params = {}

        for p in parts:
            key, value = p.strip().split('=', 1)
            params[key] = value.encode('utf-8')

        if media_type == 'application/json':
            return json.loads(self.body)
        elif media_type == 'application/x-www-form-urlencoded':
            return QueryList(urllib.parse.parse_qsl(self.body))
        elif media_type == 'multipart/form-data':
            return cgi.parse_multipart(
                BytesIO(self.body.encode('utf-8')),
                params
            )
