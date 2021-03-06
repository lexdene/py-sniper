from sniper.controllers import Controller
from sniper.exceptions import BadRequest
from sniper.responses import Response
from sniper.tests import TestApp, TestCase, TestClient
from sniper.url import url


class HelloCtrl(Controller):
    def handle(self):
        return Response('hello\n')


class BadRequestCtrl(Controller):
    def handle(self):
        raise BadRequest()


class CoverBadRequestCtrl(Controller):
    def handle(self):
        raise BadRequest()

    def handle_http_error(self, e):
        if isinstance(e, BadRequest):
            return Response(
                'cover bad request'
            )

        return super().handle_http_error(e)


app = TestApp(
    urls=[
        url(r'^/hello$', HelloCtrl),
        url(r'^/bad-request$', BadRequestCtrl),
        url(r'^/cover-bad-request$', CoverBadRequestCtrl),
    ]
)


class TestMiddleware(TestCase):
    def setUp(self):
        self.app = app
        self.client = TestClient(app)

    async def test_hello(self):
        r = await self.client.get('/hello')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'hello\n'
        )

    async def test_bad_request(self):
        r = await self.client.get('/bad-request')
        self.assertEqual(
            r.status_code,
            400
        )
        self.assertEqual(
            r.body,
            'bad request'
        )

    async def test_cover_bad_request(self):
        r = await self.client.get('/cover-bad-request')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'cover bad request'
        )
