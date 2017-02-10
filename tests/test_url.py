from sniper.controllers import Controller
from sniper.responses import Response
from sniper.tests import TestApp, TestCase, TestClient, run_coroutine
from sniper.url import include, resource, url


class TestCtrl(Controller):
    def run(self):
        return Response('Hello world!\n')


class TestPostOnlyCtrl(Controller):
    def run(self):
        return Response('method is %s\n' % self.request.method)


class TestChildCtrl(Controller):
    def run(self):
        return Response('Hello from child!\n')


class UserCtrl(Controller):
    def run(self):
        return Response(
            'action = %s, pk = %s\n' % (
                self.kwargs.get('action', ''),
                self.kwargs.get('pk', ''),
            )
        )


sub_urls = [
    url(r'^/child$', TestChildCtrl),
]

urls = [
    url(r'^/test$', TestCtrl),
    url(r'^/test/post-only$', TestPostOnlyCtrl, method='POST'),
    url(r'^/test', include(sub_urls)),
    resource(
        'users',
        UserCtrl,
    ),
]

app = TestApp(urls=urls)


class TestUrl(TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def testTest(self):
        self.assertEqual(1, 1)

    @run_coroutine
    async def testSimpleGet(self):
        r = await self.client.get('/test')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'Hello world!\n'
        )

    @run_coroutine
    async def testNotFound(self):
        r = await self.client.get('/test/xxx')
        self.assertEqual(
            r.status_code,
            404
        )

    @run_coroutine
    async def testPostPostOnlySuccess(self):
        r = await self.client.post('/test/post-only')
        self.assertEqual(
            r.status_code,
            200
        )

    @run_coroutine
    async def testGetPostOnlyNotFound(self):
        r = await self.client.get('/test/post-only')
        self.assertEqual(
            r.status_code,
            404
        )

    @run_coroutine
    async def testIncludeUrl(self):
        r = await self.client.get('/test/child')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'Hello from child!\n'
        )

    @run_coroutine
    async def testResourceRetrive(self):
        r = await self.client.get('/users/123')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'action = retrieve, pk = 123\n'
        )

    @run_coroutine
    async def testResourceDestroy(self):
        r = await self.client.delete('/users/123')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'action = destroy, pk = 123\n'
        )

    @run_coroutine
    async def testResourceList(self):
        r = await self.client.get('/users')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'action = list, pk = \n'
        )

    @run_coroutine
    async def testResourceCreate(self):
        r = await self.client.post('/users')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'action = create, pk = \n'
        )

    @run_coroutine
    async def testResourceActionNotFound(self):
        r = await self.client.delete('/users')
        self.assertEqual(
            r.status_code,
            404
        )
