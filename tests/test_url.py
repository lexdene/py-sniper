from sniper.controllers import BaseController, Controller
from sniper.responses import Response
from sniper.tests import TestApp, TestCase, TestClient, run_coroutine
from sniper.url import collection, detail, include, resource, url


def test(request):
    return Response('Hello world!')


def test_url_param(request, name):
    return Response('name is %s.' % name)


class TestPostOnlyCtrl(BaseController):
    def run(self):
        return Response('method is %s' % self.request.method)


class TestChildCtrl(BaseController):
    def run(self):
        return Response('Hello from child!')


def item_ctrl(request, action, pk='', resource_base_path=''):
    if pk:
        return Response(
            'items: %s %s' % (
                action, pk
            )
        )
    else:
        return Response(
            'items: %s' % action
        )


class UserCtrl(BaseController):
    def run(self):
        action = self.kwargs.get('action', '')
        pk = self.kwargs.get('pk', '')

        if pk:
            return Response(
                'users: %s %s' % (
                    action, pk
                )
            )
        else:
            return Response(
                'users: %s' % action
            )


class ArticleCtrl(Controller):
    def retrieve(self):
        return Response('articles: retrieve %s' % self.kwargs['pk'])

    def destroy(self):
        return Response('articles: destroy %s' % self.kwargs['pk'])

    def edit(self):
        return Response('articles: edit %s' % self.kwargs['pk'])

    def list(self):
        return Response('articles: list')

    def create(self):
        return Response('articles: create')

    def new(self):
        return Response('articles: new')

    def foo(self):
        return Response('articles: foo')

    def bar(self):
        return Response('articles: bar %s' % self.kwargs['pk'])


sub_urls_1 = [
    url(r'^/child$', TestChildCtrl),
]

sub_urls_2 = [
    url(r'^/foo$', data={'name': 'foo'}),
    url(r'^/bar$', data={'name': 'bar'}),
    url(r'^/baz$', test),
]

urls = [
    url(r'^/test$', test),
    url(r'^/test/post-only$', TestPostOnlyCtrl, method='POST'),
    include(r'^/test', sub_urls_1),
    include(r'^/test-name', sub_urls_2, controller=test_url_param),
    url(r'^/test-url-param/(?P<name>\w+)$', test_url_param),
    url(r'^/test-url-data$', test_url_param, data={'name': 'Elephant'}),
    resource(
        'items',
        item_ctrl,
        actions=[
            collection.get('foo'),
            detail.post('bar'),
        ],
    ),
    resource(
        'users',
        UserCtrl,
        actions=[
            collection.get('foo'),
            detail.post('bar'),
        ],
    ),
    resource(
        'articles',
        ArticleCtrl,
        actions=[
            collection.get('foo'),
            detail.post('bar'),
        ],
    ),
]

app = TestApp(urls=urls)


class TestUrl(TestCase):
    def setUp(self):
        self.app = app
        self.client = TestClient(app)

    @run_coroutine
    async def test_simple_get(self):
        r = await self.client.get('/test')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'Hello world!'
        )

    @run_coroutine
    async def test_not_found(self):
        r = await self.client.get('/test/xxx')
        self.assertEqual(
            r.status_code,
            404
        )

    @run_coroutine
    async def test_post_post_only_success(self):
        r = await self.client.post('/test/post-only')
        self.assertEqual(
            r.status_code,
            200
        )

    @run_coroutine
    async def test_get_post_only_not_found(self):
        r = await self.client.get('/test/post-only')
        self.assertEqual(
            r.status_code,
            404
        )

    @run_coroutine
    async def test_url_param(self):
        r = await self.client.get('/test-url-param/Elephant')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'name is Elephant.'
        )

    @run_coroutine
    async def test_url_data(self):
        r = await self.client.get('/test-url-data')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'name is Elephant.'
        )


class TestInclude(TestCase):
    def setUp(self):
        self.app = app
        self.client = TestClient(app)

    @run_coroutine
    async def test_include_url(self):
        r = await self.client.get('/test/child')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'Hello from child!'
        )

    @run_coroutine
    async def test_include_url_with_controller(self):
        for name in ('foo', 'bar'):
            with self.subTest(name=name):
                r = await self.client.get('/test-name/%s' % name)
                self.assertEqual(
                    r.status_code,
                    200
                )
                self.assertEqual(
                    r.body,
                    'name is %s.' % name
                )

    @run_coroutine
    async def test_include_url_with_inner_controller(self):
        r = await self.client.get('/test-name/baz')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'Hello world!'
        )


class TestResource(TestCase):
    def setUp(self):
        self.app = app
        self.client = TestClient(app)

    @run_coroutine
    async def test_resource_retrieve(self):
        for name in ('items', 'users', 'articles'):
            with self.subTest(name=name):
                r = await self.client.get('/%s/123' % name)
                self.assertEqual(
                    r.status_code,
                    200
                )
                self.assertEqual(
                    r.body,
                    '%s: retrieve 123' % name
                )

    @run_coroutine
    async def test_resource_destroy(self):
        for name in ('items', 'users', 'articles'):
            with self.subTest(name=name):
                r = await self.client.delete('/%s/123' % name)
                self.assertEqual(
                    r.status_code,
                    200
                )
                self.assertEqual(
                    r.body,
                    '%s: destroy 123' % name
                )

    @run_coroutine
    async def test_resource_edit(self):
        for name in ('items', 'users', 'articles'):
            with self.subTest(name=name):
                r = await self.client.get('/%s/123/edit' % name)
                self.assertEqual(
                    r.status_code,
                    200
                )
                self.assertEqual(
                    r.body,
                    '%s: edit 123' % name
                )

    @run_coroutine
    async def test_resource_list(self):
        for name in ('items', 'users', 'articles'):
            with self.subTest(name=name):
                r = await self.client.get('/%s' % name)
                self.assertEqual(
                    r.status_code,
                    200
                )
                self.assertEqual(
                    r.body,
                    '%s: list' % name
                )

    @run_coroutine
    async def test_resource_create(self):
        for name in ('items', 'users', 'articles'):
            with self.subTest(name=name):
                r = await self.client.post('/%s' % name)
                self.assertEqual(
                    r.status_code,
                    200
                )
                self.assertEqual(
                    r.body,
                    '%s: create' % name
                )

    @run_coroutine
    async def test_resource_new(self):
        for name in ('items', 'users', 'articles'):
            with self.subTest(name=name):
                r = await self.client.get('/%s/new' % name)
                self.assertEqual(
                    r.status_code,
                    200
                )
                self.assertEqual(
                    r.body,
                    '%s: new' % name
                )

    @run_coroutine
    async def test_resource_action_not_found(self):
        for name in ('items', 'users', 'articles'):
            with self.subTest(name=name):
                r = await self.client.delete('/%s' % name)
                self.assertEqual(
                    r.status_code,
                    404
                )

    @run_coroutine
    async def test_collection_action(self):
        for name in ('items', 'users', 'articles'):
            with self.subTest(name=name):
                r = await self.client.get('/%s/foo' % name)
                self.assertEqual(
                    r.status_code,
                    200
                )
                self.assertEqual(
                    r.body,
                    '%s: foo' % name
                )

    @run_coroutine
    async def test_collection_action_wrong_method_not_found(self):
        for name in ('items', 'users', 'articles'):
            with self.subTest(name=name):
                r = await self.client.post('/%s/foo' % name)
                self.assertEqual(
                    r.status_code,
                    404
                )

    @run_coroutine
    async def test_detail_action(self):
        for name in ('items', 'users', 'articles'):
            with self.subTest(name=name):
                r = await self.client.post('/%s/123/bar' % name)
                self.assertEqual(
                    r.status_code,
                    200
                )
                self.assertEqual(
                    r.body,
                    '%s: bar 123' % name
                )

    @run_coroutine
    async def test_detail_action_wrong_method_not_found(self):
        for name in ('items', 'users', 'articles'):
            with self.subTest(name=name):
                r = await self.client.get('/%s/123/bar' % name)
                self.assertEqual(
                    r.status_code,
                    404
                )
