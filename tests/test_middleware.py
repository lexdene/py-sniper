from sniper.controllers import Controller
from sniper.exceptions import BadRequest
from sniper.responses import Response
from sniper.tests import TestApp, TestCase, TestClient, run_coroutine
from sniper.url import url


class HelloCtrl(Controller):
    def handle(self):
        return Response('hello\n')


class BadRequestCtrl(Controller):
    def handle(self):
        raise BadRequest()


app = TestApp(
    urls=[
        url(r'^/hello$', HelloCtrl),
        url(r'^/bad-request$', BadRequestCtrl),
    ]
)


class TestMiddleware(TestCase):
    def setUp(self):
        self.app = app
        self.client = TestClient(app)

    @run_coroutine
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

    @run_coroutine
    async def test_bad_request(self):
        r = await self.client.get('/bad-request')
        self.assertEqual(
            r.status_code,
            400
        )
