import json
from http.cookies import SimpleCookie

from .http import ContentType, Url, parse_multipart
from .utils import QueryList, cached_property


class Request:
    def __init__(self, app, method, uri, headers=None, body=None):
        self.app = app
        self.method = method.upper()
        self.raw_uri = uri
        self.headers = QueryList(headers or [])
        self.body = body or b''

        assert isinstance(self.body, bytes), 'body must be bytes'

        # url
        self.url = Url.from_uri(
            uri,
            host=self.headers.get('Host')
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
    def content_type(self):
        s = self.headers.get('Content-Type')

        return ContentType.parse_str(s)

    @cached_property
    def data(self):
        content_type = self.content_type
        media_type = content_type.media_type

        if media_type == 'application/json':
            return json.loads(
                self.body.decode(
                    content_type.params.get('charset', 'utf-8')
                )
            )
        elif media_type == 'application/x-www-form-urlencoded':
            return QueryList.parse_str(self.body.decode('ascii'))
        elif media_type == 'multipart/form-data':
            return parse_multipart(self.body, content_type.params)
