import asyncio
import logging

from .parsers import HttpParser, RawHttpResponse
from .requests import Request
from .controllers import NotFoundController


logger = logging.getLogger('sniper.application')


class BaseApp:
    pass


class Application(BaseApp):
    def __init__(self, urls=[], config=None):
        self.urls = urls
        self.config = config

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.startup(loop))

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

    async def startup(self, loop):
        parser_class = HttpParser  # TODO: parser_class in configs
        await asyncio.start_server(
            parser_class(self.process_request),
            port='8080',
        )

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
        request = Request.build_from_raw_request(request)

        find_result = self.find_controller(request)
        if find_result:
            controller_class, url_params = find_result
        else:
            controller_class = NotFoundController
            argv = []
            kwargs = {}

        controller = controller_class(request, url_params)
        response = controller.run()

        return response.build_raw_response()

    def find_controller(self, request):
        for url in self.urls:
            match = url.router.match(request, {})
            if match:
                return url.controller, match


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
