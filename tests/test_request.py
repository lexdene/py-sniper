import json

from sniper.responses import Response
from sniper.tests import TestApp, TestCase, TestClient
from sniper.url import url


def get_name_from_data(request):
    return Response('name = %s\n' % request.data.get('name', 'Elephant'))


app = TestApp(
    urls=[
        url(r'^/test-name-from-data$', get_name_from_data),
    ]
)


class TestRequestData(TestCase):
    def setUp(self):
        self.app = app
        self.client = TestClient(app)

    async def test_json_data(self):
        r = await self.client.post(
            '/test-name-from-data',
            headers=[
                ('Content-Type', 'application/json'),
            ],
            body=json.dumps({
                'name': 'Thomas'
            })
        )
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'name = Thomas\n'
        )

    async def test_urlencoded(self):
        r = await self.client.post(
            '/test-name-from-data',
            headers=[
                ('Content-Type', 'application/x-www-form-urlencoded'),
            ],
            body='hello=world&name=Tommy'
        )
        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'name = Tommy\n'
        )
