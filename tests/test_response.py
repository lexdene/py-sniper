from sniper.responses import Response
from sniper.tests import TestApp, TestCase, TestClient
from sniper.url import url


def test_empty_response(request):
    return Response()


urls = [
    url(r'^/test-empty-response', test_empty_response),
]

app = TestApp(urls=urls)


class TestResponse(TestCase):
    def setUp(self):
        self.app = app
        self.client = TestClient(app)

    async def test_empty_response(self):
        r = await self.client.get('/test-empty-response')
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            ''
        )
