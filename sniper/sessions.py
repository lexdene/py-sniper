import datetime

from .utils import random_string


class BaseSession:
    COOKIE_NAME = 'sessionid'
    EXPIRE_DAYS = 7

    def __init__(self, request, store):
        self.request = request
        self.store = store

        self._data = None
        self._key = None
        self._edited = False
        self._is_new = True

    def is_data_valid(self, data):
        return True

    @property
    def data(self):
        if self._data is None:
            self._data, self._key, self._is_new = self._load_session()

        return self._data

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self._edited = True

    def _load_session(self):
        'return (data, session_key, is_new)'
        cookie_name = self.get_cookie_name()
        session_key = self.request.cookie.get(cookie_name, None)

        if session_key:
            data = self.get_by_key(session_key)
            if data and self.is_data_valid(data):
                return data, session_key, False

        return {}, None, True

    def get_by_key(self, key):
        data = self.store.get(key)
        if data and data['expire_at'] > datetime.datetime.now() \
                and data['key'] == key:
            return data['data']

    def flush(self, response):
        if self._edited:
            cookie_name = self.get_cookie_name()
            session_key = self.request.cookie.get(cookie_name, None)
            if self._key is None:
                self._key = random_string(length=32)

            if self._key != session_key:
                response.cookies[cookie_name] = self._key

            expire_at = datetime.datetime.now() + self.get_expire_length()
            if self._is_new:
                self.store.create(
                    key=self._key,
                    data=self._data,
                    expire_at=expire_at,
                )
            else:
                self.store.update(
                    key=self._key,
                    data=self._data,
                    expire_at=expire_at,
                )

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

    request.session = session_cls(request, store)
    response = await get_response(controller)
    request.session.flush(response)

    return response
