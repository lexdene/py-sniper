from sniper.authentications import BaseAuthentication
from sniper.controllers import Controller
from sniper.tests import TestApp, TestCase, TestClient
from sniper.url import url

USER_DATA = [
    {
        'id': 1,
        'name': 'Peter',
        'token': 'l5eqrewsksn68u08',
    },
]


class TestAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get('Authorization', '').split()
        print('auth:', auth)

        if not auth or len(auth) != 2:
            return

        auth_type, auth_value = auth
        if auth_type != 'Token':
            return

        for u in USER_DATA:
            if u['token'] == auth_value:
                print(u)
                return u


class TestController(Controller):
    authentication_classes = (
        TestAuthentication,
    )

    def handle(self):
        user = self.user
        print('user in handle:', user)

        if user:
            return 'user id is %s, name is %s.' % (
                user['id'],
                user['name'],
            )
        else:
            return 'not authenticated'


app = TestApp(
    urls=[
        url(r'^/$', TestController),
    ]
)


class TestAuthenticationTestCase(TestCase):
    def setUp(self):
        self.app = app
        self.client = TestClient(app)

    async def test_not_authenticated(self):
        r = await self.client.get('/')

        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'not authenticated'
        )

    async def test_authenticate_success(self):
        r = await self.client.get(
            '/',
            headers=[
                ('Authorization', 'Token l5eqrewsksn68u08'),
            ]
        )

        self.assertEqual(
            r.status_code,
            200
        )
        self.assertEqual(
            r.body,
            'user id is 1, name is Peter.'
        )
