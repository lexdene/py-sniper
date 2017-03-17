import cgi
import urllib.parse
from collections import namedtuple
from io import BytesIO

from .utils import QueryList

UrlStruct = namedtuple(
    'UrlStruct',
    ['scheme', 'host', 'path', 'query'],
)


class Url(UrlStruct):
    def copy(self):
        data = {}

        for name in self._fields:
            value = getattr(self, name)
            if name == 'query':
                value = value.copy()

            data[name] = value

        return self.__class__(**data)

    def replace_query(self, **kwargs):
        for key, value in kwargs.items():
            self.query.set(key, value)

        return self

    def to_uri(self):
        return '%s?%s' % (
            self.path,
            urllib.parse.urlencode(
                list(self.query.items())
            )
        )

    @classmethod
    def from_uri(cls, uri, host=None):
        parse_result = urllib.parse.urlparse(uri)

        if host is None:
            host = parse_result.netloc

        return cls(
            scheme=parse_result.scheme,
            host=host,
            path=parse_result.path,
            query=QueryList.parse_str(parse_result.query),
        )


class ContentType:
    def __init__(self, media_type, params):
        assert isinstance(params, QueryList), (
            'params must be QueryList'
        )

        self.media_type = media_type
        self.params = params

    @classmethod
    def parse_str(cls, s):
        parts = s.split(';')
        media_type = parts.pop(0)

        params = QueryList([
            tuple(p.strip().split('=', 1))
            for p in parts
        ])

        return cls(media_type, params)


def parse_multipart(body, params):
    return cgi.parse_multipart(
        BytesIO(body),
        {
            key: value.encode('ascii')
            for key, value in params.items()
        }
    )
