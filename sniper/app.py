import asyncio
import logging

from .controllers import BaseController, NotFoundController
from .parsers import HttpParser, RawHttpResponse
from .requests import Request

logger = logging.getLogger('sniper.application')


class BaseApp:
    def __init__(self, urls=[], config=None):
        self.urls = urls
        self.config = config

        self.loop = asyncio.get_event_loop()

    async def process_request(self, request):
        try:
            response = await self.get_response(request)
        except Exception as e:
            logger.exception(e)
            response = self._build_response_for_exception(request, e)

        logger.info(
            '%s %s %d',
            request.method,
            request.uri,
            response.status_code
        )
        return response

    async def get_response(self, request):
        request = Request.build_from_raw_request(request, self)

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

        return result.build_raw_response()

    def find_controller(self, request):
        for url in self.urls:
            match = url.match({'request': request})
            if match:
                return match

    def _build_response_for_exception(self, request, exception):
        body = str(exception) + '\n'

        response = RawHttpResponse(
            http_version='1.1',
            status_code=500,
            reason_phrase="inter server error",
            headers=[
                ('Content-Length', len(body)),
            ],
            body=body,
        )
        return response


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
            parser_class(self.process_request),
            port=port,
        )
        logger.info('server started on port %s' % port)
