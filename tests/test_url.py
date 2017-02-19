from sniper.controllers import BaseController, Controller
from sniper.responses import Response
from sniper.tests import TestApp, TestCase, TestClient, run_coroutine
from sniper.url import collection, detail, include, resource, url


def test(request):
    return Response('Hello world!\n')


def test_url_param(request, name):
    return Response('name is %s.\n' % name)


class TestPostOnlyCtrl(BaseController):
    def run(self):
        return Response('method is %s\n' % self.request.method)


class TestChildCtrl(BaseController):
    def run(self):
        return Response('Hello from child!\n')


class UserCtrl(BaseController):
    def run(self):
        return Response(
            'action = %s, pk = %s\n' % (
                self.kwargs.get('action', ''),
                self.kwargs.get('pk', ''),
            )
        )


class ArticleCtrl(Controller):
    def retrieve(self):
        return 'article retrieve %s\n' % self.kwargs['pk']

    def list(self):
        return 'article list\n'

    def hot(self):
        return 'get hot articles\n'

    def vote(self):
        return 'vote article %s\n' % self.kwargs['pk']


sub_urls = [
    url(r'^/child$', TestChildCtrl),
]

urls = [
    url(r'^/test$', test),
    url(r'^/test/post-only$', TestPostOnlyCtrl, method='POST'),
    url(r'^/test', include(sub_urls)),
    url(r'^/test-url-param/(?P<name>\w+)$', test_url_param),
    url(r'^/test-url-data$', test_url_param, data={'name': 'Elephant'}),
    resource(
        'users',
        UserCtrl,
        actions=[
            collection.get('hot'),
            detail.post('connect'),
        ],
    ),
    resource(
        'articles',
        ArticleCtrl,
        actions=[
            collection.get('hot'),
            detail.post('vote'),
        ],
    ),
]

app = TestApp(urls=urls)


class TestUrl(TestCase):
    def setUp(self):
        self.app = app
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
    async def testUrlParam(self):
        r = await self.client.get('/test-url-param/Elephant')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'name is Elephant.\n'
        )

    @run_coroutine
    async def testUrlData(self):
        r = await self.client.get('/test-url-data')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'name is Elephant.\n'
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

    @run_coroutine
    async def testGetUsersHot(self):
        r = await self.client.get('/users/hot')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'action = hot, pk = \n'
        )

    @run_coroutine
    async def testPostUsersHotNotFound(self):
        r = await self.client.post('/users/hot')
        self.assertEqual(
            r.status_code,
            404
        )

    @run_coroutine
    async def testGetUserConnectNotFound(self):
        r = await self.client.get('/users/123/connect')
        self.assertEqual(
            r.status_code,
            404
        )

    @run_coroutine
    async def testPostUserConnect(self):
        r = await self.client.post('/users/123/connect')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'action = connect, pk = 123\n'
        )

    @run_coroutine
    async def testGetArticleRetrieveSuccess(self):
        r = await self.client.get('/articles/123')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'article retrieve 123\n'
        )

    @run_coroutine
    async def testGetArticleListSuccess(self):
        r = await self.client.get('/articles')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'article list\n'
        )

    @run_coroutine
    async def testGetArticlesHot(self):
        r = await self.client.get('/articles/hot')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'get hot articles\n'
        )

    @run_coroutine
    async def testPostArticlesHotNotFound(self):
        r = await self.client.post('/articles/hot')
        self.assertEqual(
            r.status_code,
            404
        )

    @run_coroutine
    async def testGetArticleConnectNotFound(self):
        r = await self.client.get('/articles/123/vote')
        self.assertEqual(
            r.status_code,
            404
        )

    @run_coroutine
    async def testPostArticleConnect(self):
        r = await self.client.post('/articles/123/vote')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'vote article 123\n'
        )
