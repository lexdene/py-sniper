import datetime

from sniper.controllers import Controller
from sniper.responses import Response
from sniper.sessions import SimpleSessionStore
from sniper.tests import TestApp, TestCase, TestClient
from sniper.url import url
from sniper.utils import get_now


class SessionNameCtrl(Controller):
    def get(self):
        return Response('name = %s\n' % self.request.session.get('name', ''))

    def set(self):
        name = self.request.data.get('name')

        if name:
            self.request.session.set('name', name)

        return Response('')


urls = [
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


class TestSessionStore(SimpleSessionStore):
    def __init__(self, app):
        self.app = app
        self.data = app.session_store_data


class TestSession(TestCase):
    def setUp(self):
        self.app = TestApp(
            urls=urls,
            config=dict(
                session_store_class=TestSessionStore
            )
        )
        self.app.session_store_data = {}
        self.client = TestClient(self.app)

    async def test_inside_expire(self):
        key = 'abcdefgh' * 4
        self.assertEqual(len(key), 32)

        now = get_now()
        self.app.session_store_data[key] = {
            'key': key,
            'data': {
                'name': 'John',
            },
            'expire_at': now + datetime.timedelta(days=1)
        }

        self.client.set_cookie('sessionid', key)
        r = await self.client.get('/get-name')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.body, 'name = John\n')

    async def test_beyond_expire(self):
        key = 'stuvwxyz' * 4
        self.assertEqual(len(key), 32)

        now = get_now()
        self.app.session_store_data[key] = {
            'key': key,
            'data': {
                'name': 'Alice',
            },
            'expire_at': now - datetime.timedelta(days=1)
        }

        self.client.set_cookie('sessionid', key)
        r = await self.client.get('/get-name')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.body, 'name = \n')

    async def test_set_name(self):
        r1 = await self.client.get('/get-name')
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.body, 'name = \n')

        r2 = await self.client.post('/set-name', data={'name': 'Peter'})
        self.assertEqual(r2.status_code, 200)

        r3 = await self.client.get('/get-name')
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(r3.body, 'name = Peter\n')
