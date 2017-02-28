from sniper.responses import Response
from sniper.tests import TestApp, TestCase, TestClient, run_coroutine
from sniper.url import url


def get_query(request):
    return Response('name = %s\n' % request.query.get('name', 'Elephant'))


def get_header(request):
    return Response(
        'X-Name = %s\n' % request.headers.get('X-Name', 'Elephant')
    )


def get_cookie(request):
    return Response(
        'name in cookie = %s\n' % request.cookie.get('name', 'Elephant')
    )


def set_header(request):
    return Response(
        '',
        headers=[
            ('X-Name', 'Elephant')
        ]
    )


def set_cookie(request):
    return Response(
        '',
        cookies={
            'name': 'Elephant'
        }
    )


def set_cookie_to_response(request):
    r = Response('')
    r.cookies['name'] = 'Elephant'
    return r


app = TestApp(
    urls=[
        url(r'^/test-query$', get_query),
        url(r'^/test-header$', get_header),
        url(r'^/test-cookie$', get_cookie),
        url(r'^/test-set-header$', set_header),
        url(r'^/test-set-cookie$', set_cookie),
        url(r'^/test-set-cookie-to-response$', set_cookie_to_response),
    ]
)


class TestHeaders(TestCase):
    def setUp(self):
        self.app = app
        self.client = TestClient(app)

    @run_coroutine
    async def test_query(self):
        r = await self.client.get('/test-query?name=Jack')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'name = Jack\n'
        )

    @run_coroutine
    async def test_header(self):
        r = await self.client.get(
            '/test-header',
            headers=[
                ('X-Name', 'Joe'),
            ]
        )
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'X-Name = Joe\n'
        )

    @run_coroutine
    async def test_cookie(self):
        r = await self.client.get(
            '/test-cookie',
            headers=[
                ('Cookie', 'name=Jane'),
            ]
        )
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'name in cookie = Jane\n'
        )

    @run_coroutine
    async def test_set_header(self):
        r = await self.client.get(
            '/test-set-header'
        )
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            dict(r.headers).get('X-Name'),
            'Elephant'
        )

    @run_coroutine
    async def test_set_cookie(self):
        r = await self.client.get(
            '/test-set-cookie'
        )
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            dict(r.headers).get('Set-Cookie'),
            'name=Elephant'
        )

    @run_coroutine
    async def test_set_cookie_to_response(self):
        r = await self.client.get(
            '/test-set-cookie-to-response'
        )
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            dict(r.headers).get('Set-Cookie'),
            'name=Elephant'
        )
