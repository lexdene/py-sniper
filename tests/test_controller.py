from sniper.controllers import Controller
from sniper.responses import Response
from sniper.tests import TestApp, TestCase, TestClient
from sniper.url import include, url


def return_response(request):
    return Response('Hello world!')


class ReturnStrCtrl(Controller):
    def handle(self):
        return 'Hello world!'


class ReturnResponseCtrl(Controller):
    def handle(self):
        return Response('Hello world!')


class HandleByHandleCtrl(Controller):
    def handle(self):
        return 'return from handle'


class HandleByActionCtrl(Controller):
    def foo(self):
        return 'return from foo'


function_controller_urls = [
    url(r'^/return-response$', return_response),
]

class_controller_urls = [
    url(r'^/return-str$', ReturnStrCtrl),
    url(r'^/return-response$', ReturnResponseCtrl),
    url(r'^/handle-by-handle$', HandleByHandleCtrl),
    url(r'^/handle-by-foo$', HandleByActionCtrl, data={'action': 'foo'}),
    url(
        r'^/handle-by-handle-with-action$',
        HandleByHandleCtrl,
        data={'action': 'foo'}
    ),
]
urls = [
    include(r'^/test-function-controller', function_controller_urls),
    include(r'^/test-class-controller', class_controller_urls),
]


class TestController(TestCase):
    def setUp(self):
        self.app = TestApp(urls=urls)
        self.client = TestClient(self.app)

    async def test_function_controller_return_type(self):
        # function controller can only return response
        for t in ('response',):
            with self.subTest(name=t):
                r = await self.client.get(
                    '/test-function-controller/return-%s' % t
                )
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.body, 'Hello world!')

    async def test_class_controller_return_type(self):
        for t in ('str', 'response'):
            with self.subTest(name=t):
                r = await self.client.get(
                    '/test-class-controller/return-%s' % t
                )
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.body, 'Hello world!')

    async def test_handle_or_action(self):
        for t in ('handle', 'foo'):
            with self.subTest(name=t):
                r = await self.client.get(
                    '/test-class-controller/handle-by-%s' % t
                )
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.body, 'return from %s' % t)

    async def test_handle_with_action(self):
        r = await self.client.get(
            '/test-class-controller/handle-by-handle-with-action'
        )
        self.assertEqual(r.status_code, 405)
