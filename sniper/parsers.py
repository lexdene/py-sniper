import asyncio
import re
from collections import namedtuple

from .requests import Request


HTTP_LINE_SEPARATOR = b'\r\n'
START_LINE_REGEXP = re.compile(
    r'^(?P<method>\w+) (?P<uri>.+) HTTP/(?P<version>[0-9.]+)$'
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
                start_line = await self._read_http_line_from_reader(
                    reader, coding='ascii'
                )
            except asyncio.IncompleteReadError:
                break

            method, uri, http_version = self._parse_start_line(start_line)

            headers = []
            content_length = 0
            # content_type = None
            # content_encoding = None

            while True:
                line = await self._read_http_line_from_reader(
                    reader, coding='utf-8'
                )
                if line == '':
                    # header part ends
                    break

                name, value = line.split(':', 1)
                value = value.strip()
                headers.append((name, value))

                if name.lower() == 'content-length':
                    content_length = int(value)
                # elif name.lower() == 'content-encoding':
                #     content_encoding = value
                # elif name.lower() == 'content-type':
                #     content_type = value

            if content_length > 0:
                body = await reader.readexactly(content_length)
                body = body.decode('utf-8')
            else:
                body = ''

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

    async def _read_http_line_from_reader(self, reader, *, coding='utf-8'):
        line = await reader.readuntil(HTTP_LINE_SEPARATOR)

        # remove separator
        line = line[:-len(HTTP_LINE_SEPARATOR)]

        # decode
        line = line.decode(coding)

        return line

    async def _write_http_line_to_writer(self, writer, data, coding='utf-8'):
        data = data.encode(coding) + HTTP_LINE_SEPARATOR
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
        return Request(
            app=self.app,
            method=raw_request.method.upper(),
            uri=raw_request.uri,
            headers=raw_request.headers,
            body=raw_request.body,
        )

    def build_raw_response(self, response):
        return _RawHttpResponse(
            http_version='1.1',
            status_code=response.status_code,
            reason_phrase=response.status_phrase,
            body=response.body,
            headers=list(response.freeze_headers.items()),
        )

    async def write_response(self, writer, response):
        await self._write_http_line_to_writer(
            writer,
            'HTTP/%s %d %s' % (
                response.http_version,
                response.status_code,
                response.reason_phrase,
            )
        )
        for name, value in response.headers:
            await self._write_http_line_to_writer(
                writer,
                '%s: %s' % (name, value),
            )
        await self._write_http_line_to_writer(writer, '')
        await writer.drain()

        writer.write(response.body.encode('utf-8'))
        await writer.drain()
