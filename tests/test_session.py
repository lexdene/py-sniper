from sniper.controllers import Controller
from sniper.responses import Response
from sniper.tests import TestApp, TestCase, TestClient
from sniper.url import url


class SessionNameCtrl(Controller):
    def get(self):
        return Response('name = %s\n' % self.request.session.get('name', ''))

    def set(self):
        name = self.request.data.get('name')

        if name:
            self.request.session.set('name', name)

        return Response('')


app = TestApp(
    urls=[
        url(
            r'^/get-name$',
            SessionNameCtrl,
            method='GET',
            data={'action': 'get'}
        ),
        url(
            r'^/set-name$',
            SessionNameCtrl,
            method='POST',
            data={'action': 'set'}
        ),
    ]
)


class TestSession(TestCase):
    def setUp(self):
        self.app = app
        self.client = TestClient(app)

    async def test_set_name(self):
        r1 = await self.client.get('/get-name')
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.body, 'name = \n')

        r2 = await self.client.post('/set-name', data={'name': 'Peter'})
        self.assertEqual(r2.status_code, 200)

        r3 = await self.client.get('/get-name')
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(r3.body, 'name = Peter\n')
