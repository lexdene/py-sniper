import asyncio
import logging
import time

from .controllers import BaseController, NotFoundController
from .parsers import HttpParser, ParseError
from .responses import Response

logger = logging.getLogger('sniper.application')


class BaseApp:
    def __init__(self, urls=[], config=None,
                 parser_class=None,
                 startups=[]):
        self.urls = urls
        self.config = config or {}

        self.parser_class = parser_class or HttpParser
        self._parser = None

        self.startups = startups

        self.next_connection_id = 0

        self.loop = asyncio.get_event_loop()

    @property
    def parser(self):
        if not self._parser:
            self._parser = self.parser_class(self)

        return self._parser

    async def process_request(self, request):
        begin_time = time.time()
        connection_id = getattr(request, 'connection_id', 0)

        logger.info(
            '%d BEGIN %s %s',
            connection_id,
            request.method,
            request.raw_uri,
        )

        try:
            response = await self.get_response(request)
        except Exception as e:
            logger.exception(e)
            response = self._build_response_for_exception(request, e)

        end_time = time.time()
        elapsed_time = end_time - begin_time
        logger.info(
            '%d %s %s %d %.2fms',
            connection_id,
            request.method,
            request.raw_uri,
            response.status_code,
            elapsed_time * 1000
        )
        return response

    async def get_response(self, request):
        result = self.resolve_request(request)
        if result:
            controller_func, argv, kwargs = result
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

    def resolve_request(self, request):
        params = {'request': request}
        for url in self.urls:
            result = url.resolve(params)
            if result:
                return result

    def _build_response_for_exception(self, request, exception):
        return Response(
            body=str(exception) + '\n',
            status_code=500,
        )


class Application(BaseApp):
    def run(self, *argv, **kwargs):
        startup_task = self.loop.create_task(self.startup(*argv, **kwargs))
        startup_task.add_done_callback(self.on_startup_done)

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

    async def startup(self, port=None, socket_path=None):
        if port:
            await asyncio.start_server(
                self._client_connected,
                port=port,
                loop=self.loop,
            )
            logger.info('server started on port %s' % (port,))
        elif socket_path:
            await asyncio.start_unix_server(
                self._client_connected,
                path=socket_path,
                loop=self.loop,
            )
            logger.info('server started on unix path %s' % (socket_path,))
        else:
            raise ValueError('one of port and socket_path must be provided.')

        for startup in self.startups:
            await startup(self.loop, self)

    def on_startup_done(self, fut):
        'exit if error when startup'
        assert fut.done(), 'startup is not done'

        err = fut.exception()
        if err:
            self.loop.stop()
            raise err

    async def _client_connected(self, reader, writer):
        connection_id = self.next_connection_id
        self.next_connection_id += 1

        logger.debug('%d connected', connection_id)
        while True:
            if reader.at_eof():
                logger.debug('%d connection closed', connection_id)
                break

            try:
                request = await self.parser.read_request(reader)
                request.connection_id = connection_id
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
