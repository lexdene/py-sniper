import urllib.parse
from collections import namedtuple

from .headers import Header


Url = namedtuple(
    'Url',
    ['scheme', 'host', 'path', 'query'],
    module=__name__,
)


class Request:
    def __init__(self, method, url, headers, body):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body

    @classmethod
    def build_from_raw_request(cls, raw_request):
        headers = Header(raw_request.headers)

        # url
        parse_result = urllib.parse.urlparse(raw_request.uri)

        if 'Host' in headers:
            host = headers['Host']
        else:
            host = parse_result.netloc

        url = Url(
            scheme=parse_result.scheme,
            host=host,
            path=parse_result.path,
            query=urllib.parse.parse_qs(parse_result.query),
        )

        return cls(
            method=raw_request.method.upper(),
            url=url,
            headers=headers,
            body=raw_request.body,
        )
