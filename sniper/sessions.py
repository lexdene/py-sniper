import datetime

from .utils import random_string


class BaseSession:
    COOKIE_NAME = 'sessionid'
    EXPIRE_DAYS = 7

    def __init__(self, key):
        self.key = key
        self._data = None

        self._edited = False
        self._new = True

    def is_valid(self, request):
        return True

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self._edited = True

    def load_data(self, data):
        self._data = data
        self._new = False

    def init_data(self, request):
        self._data = {}
        self._new = True

    def save(self, store):
        if not self._edited:
            return

        if self._new:
            store.create(
                key=self.key,
                data=self._data,
                expire_at=datetime.datetime.now() + self.get_expire_length()
            )
        else:
            store.update(
                key=self.key,
                data=self._data,
                expire_at=datetime.datetime.now() + self.get_expire_length()
            )

    @classmethod
    def get_by_key(cls, key, store):
        data = store.get(key)
        if data:
            if data['expire_at'] > datetime.datetime.now():
                s = cls(key)
                s.load_data(data['data'])
                return s

    @classmethod
    def create(cls, request):
        key = random_string(length=32)
        s = cls(key)
        s.init_data(request)
        return s

    @classmethod
    def get_cookie_name(cls):
        return cls.COOKIE_NAME

    @classmethod
    def get_expire_length(cls):
        return datetime.timedelta(days=cls.EXPIRE_DAYS)


class BaseSessionStore:
    def get(self, key):
        '''
            return a dict or None
                {
                    'key': key,
                    'data': {},
                    'expire_at': datetime.datetime(
                        2017, 3, 2, 18, 27, 11, 257436
                    ),
                }
        '''
        raise NotImplementedError

    def create(self, key, data, expire_at):
        raise NotImplementedError

    def update(self, key, data, expire_at):
        raise NotImplementedError


class SimpleSessionStore(BaseSessionStore):
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key, None)

    def create(self, key, data, expire_at):
        return self.update(key, data, expire_at)

    def update(self, key, data, expire_at):
        self.data[key] = {
            'key': key,
            'data': data,
            'expire_at': expire_at
        }


async def session_middleware(controller, get_response):
    app = controller.app
    request = controller.request

    if app.session_cls is None:
        app.session_cls = BaseSession

    if app.session_store is None:
        app.session_store = SimpleSessionStore()

    session_cls = app.session_cls
    store = app.session_store
    cookie_name = session_cls.get_cookie_name()

    session_key = request.cookie.get(cookie_name, None)
    if session_key:
        session = session_cls.get_by_key(session_key, store)
    else:
        session = None

    if session is None or not session.is_valid(controller.request):
        session = session_cls.create(request)

    request.session = session
    response = await get_response(controller)

    if session.key != session_key and session._edited:
        response.cookies[cookie_name] = session.key

    session.save(store)

    return response
