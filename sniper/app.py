import asyncio
import logging

from .controllers import BaseController, NotFoundController
from .parsers import HttpParser
from .responses import Response

logger = logging.getLogger('sniper.application')


class BaseApp:
    def __init__(self, urls=[], config=None,
                 session_cls=None, session_store=None):
        self.urls = urls
        self.config = config

        self.session_cls = session_cls
        self.session_store = session_store

        self.loop = asyncio.get_event_loop()

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
        parser_class = HttpParser  # TODO: parser_class in configs
        await asyncio.start_server(
            parser_class(self, self.process_request),
            port=port,
        )
        logger.info('server started on port %s' % port)
