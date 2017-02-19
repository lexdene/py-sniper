from sniper.controllers import BaseController, Controller
from sniper.responses import Response
from sniper.tests import TestApp, TestCase, TestClient, run_coroutine
from sniper.url import resource, url


def set_future_result(f, data):
    f.set_result(data.upper())


def simple_coroutine_function(loop, data):
    f = loop.create_future()
    loop.call_later(0, set_future_result, f, data)
    return f


async def test(request):
    data = await simple_coroutine_function(
        request.app.loop,
        'hello test'
    )
    return Response('data is %s\n' % data)


class TestController(BaseController):
    async def run(self):
        data = await simple_coroutine_function(
            self.request.app.loop,
            'hello run'
        )
        return Response('data is %s\n' % data)


class ArticleCtrl(Controller):
    async def retrieve(self):
        data = await simple_coroutine_function(
            self.request.app.loop,
            'article retrieve %s' % self.kwargs['pk']
        )
        return 'data is %s\n' % data


urls = [
    url(r'^/test$', test),
    url(r'^/test-controller$', TestController),
    resource('articles', ArticleCtrl),
]
app = TestApp(urls=urls)


class TestCoroutineController(TestCase):
    def setUp(self):
        self.app = app
        self.client = TestClient(app)

    @run_coroutine
    async def testSimpleCoroutineFunction(self):
        result = await simple_coroutine_function(
            self.app.loop,
            'hello'
        )
        self.assertEqual(
            result,
            'HELLO'
        )

    @run_coroutine
    async def testCoroutineControllerFunction(self):
        r = await self.client.get('/test')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'data is HELLO TEST\n'
        )

    @run_coroutine
    async def testCoroutineController(self):
        r = await self.client.get('/test-controller')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'data is HELLO RUN\n'
        )

    @run_coroutine
    async def testCoroutineResource(self):
        r = await self.client.get('/articles/xxx')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'data is ARTICLE RETRIEVE XXX\n'
        )
