import asyncio
import re
from collections import namedtuple

from .requests import Request


HEADER_ENCODING = 'ascii'  # am i right?
HTTP_LINE_SEPARATOR = b'\r\n'
START_LINE_REGEXP = re.compile(
    br'^(?P<method>\w+) (?P<uri>.+) HTTP/(?P<version>[0-9.]+)$'
)


class ParseError(ValueError):
    pass


_RawHttpRequest = namedtuple(
    'RawHttpRequest',
    ['method', 'uri', 'http_version', 'headers', 'body'],
)
_RawHttpResponse = namedtuple(
    'RawHttpResponse',
    ['http_version', 'status_code', 'reason_phrase', 'headers', 'body'],
)


class BaseParser:
    pass


class HttpParser(BaseParser):
    def __init__(self, app, process_func):
        self.app = app
        self.process_func = process_func

    async def __call__(self, reader, writer):
        while True:
            try:
                start_line = await self._read_http_line_from_reader(reader)
            except asyncio.IncompleteReadError:
                break

            method, uri, http_version = self._parse_start_line(start_line)

            headers = []
            content_length = 0

            while True:
                line = await self._read_http_line_from_reader(reader)
                if not line:
                    # header part ends
                    break

                name, value = line.split(b':', 1)
                value = value.strip()
                headers.append((name, value))

                if name.lower() == b'content-length':
                    content_length = int(value)

            if content_length > 0:
                body = await reader.readexactly(content_length)
            else:
                body = b''

            request = _RawHttpRequest(
                method=method,
                uri=uri,
                http_version=http_version,
                headers=headers,
                body=body,
            )
            request = self.build_request(request)

            response = await self.process_func(request)
            response = self.build_raw_response(response)

            await self.write_response(writer, response)

    async def _read_http_line_from_reader(self, reader):
        line = await reader.readuntil(HTTP_LINE_SEPARATOR)

        # remove separator
        line = line[:-len(HTTP_LINE_SEPARATOR)]

        return line

    async def _write_http_line_to_writer(self, writer, data):
        # append separator
        data = data + HTTP_LINE_SEPARATOR

        writer.write(data)

    def _parse_start_line(self, start_line):
        match = START_LINE_REGEXP.match(start_line)

        if match:
            return (
                match.group('method'),
                match.group('uri'),
                match.group('version'),
            )
        else:
            raise ParseError('can not parse start line', start_line)

    def build_request(self, raw_request):
        '''
            build a requests.Request object.
            everything in raw_request are bytes.
        '''

        kwargs = {}
        for key in ('method', 'uri'):
            kwargs[key] = getattr(raw_request, key).decode(HEADER_ENCODING)

        headers = [
            (key.decode(HEADER_ENCODING), value.decode(HEADER_ENCODING))
            for key, value in raw_request.headers
        ]

        return Request(
            app=self.app,
            headers=headers,
            body=raw_request.body,
            **kwargs
        )

    def build_raw_response(self, response):
        '''
            build a _RawHttpResponse object.
            most of _RawHttpresponse are bytes except status_code.
        '''
        body = response.body
        if isinstance(body, str):
            body = body.encode(response.charset)

        return _RawHttpResponse(
            http_version=b'1.1',
            status_code=response.status_code,
            reason_phrase=response.status_phrase.encode(HEADER_ENCODING),
            body=body,
            headers=[
                (key.encode(HEADER_ENCODING), value.encode(HEADER_ENCODING))
                for key, value in response.freeze_headers().items()
            ],
        )

    async def write_response(self, writer, response):
        await self._write_http_line_to_writer(
            writer,
            b'HTTP/%s %d %s' % (
                response.http_version,
                response.status_code,
                response.reason_phrase,
            )
        )
        for name, value in response.headers:
            await self._write_http_line_to_writer(
                writer,
                b'%s: %s' % (name, value),
            )
        await self._write_http_line_to_writer(writer, b'')
        await writer.drain()

        writer.write(response.body)
        await writer.drain()
