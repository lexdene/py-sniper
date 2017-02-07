import asyncio

from . import parsers


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
        await asyncio.start_server(
            parsers.HttpParser(self.process_request),
            port='8080',
        )

    async def process_request(self, request):
        print('%s %s' % (request.method, request.uri))
        body = "Nick to meet you!"

        return parsers.RawHttpResponse(
            http_version=request.http_version,
            status_code=200,
            reason_phrase="Let's rock and roll",
            headers=[
                ('Content-Length', len(body)),
            ],
            body=body,
        )
