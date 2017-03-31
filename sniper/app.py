import asyncio
import logging

from .controllers import BaseController, NotFoundController
from .parsers import HttpParser
from .responses import Response

logger = logging.getLogger('sniper.application')


class BaseApp:
    def __init__(self, urls=[], config=None,
                 session_cls=None, session_store=None,
                 parser_class=None):
        self.urls = urls
        self.config = config

        self.session_cls = session_cls
        self.session_store = session_store

        self.parser_class = parser_class or HttpParser
        self._parser = None

        self.loop = asyncio.get_event_loop()

    @property
    def parser(self):
        if not self._parser:
            self._parser = self.parser_class(self)

        return self._parser

    async def process_request(self, request):
        logger.info(
            'BEGIN %s %s',
            request.method,
            request.raw_uri,
        )

        try:
            response = await self.get_response(request)
        except Exception as e:
            logger.exception(e)
            response = self._build_response_for_exception(request, e)

        logger.info(
            '%s %s %d',
            request.method,
            request.raw_uri,
            response.status_code
        )
        return response

    async def get_response(self, request):
        find_result = self.find_controller(request)
        if find_result:
            controller_func, argv, kwargs = find_result
        else:
            controller_func = NotFoundController
            argv = []
            kwargs = {}

        result = controller_func(request, *argv, **kwargs)
        if isinstance(result, BaseController):
            result = result.run()

        if asyncio.iscoroutine(result):
            result = await result

        return result

    def find_controller(self, request):
        for url in self.urls:
            match = url.match({'request': request})
            if match:
                return match

    def _build_response_for_exception(self, request, exception):
        return Response(
            body=str(exception) + '\n',
            status_code=500,
        )


class Application(BaseApp):
    def run(self, port):
        self.loop.run_until_complete(self.startup(port))

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

    async def startup(self, port):
        await asyncio.start_server(
            self._client_connected,
            port=port,
            loop=self.loop,
        )
        logger.info('server started on port %s' % port)

    async def _client_connected(self, reader, writer):
        while True:
            if reader.at_eof():
                logger.debug('connection closed')
                break

            try:
                request = await self.parser.read_request(reader)
                resp = await self.process_request(request)
                await self.parser.write_response(writer, resp)
            except asyncio.IncompleteReadError:
                writer.close()
            except Exception as e:
                logger.exception(e)

                if isinstance(e, ParseError):
                    status_code = 400
                else:
                    status_code = 500

                resp = Response(
                    body=str(e) + '\n',
                    status_code=status_code,
                )
                await self.parser.write_response(writer, resp)
                writer.close()
