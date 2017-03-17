import urllib.parse
from collections import namedtuple

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
