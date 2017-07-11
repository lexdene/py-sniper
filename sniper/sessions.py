import datetime
from email.utils import format_datetime

from .utils import get_now, random_string


class Session:
    def __init__(self, request, engine):
        self.request = request
        self.engine = engine

        self._key = None
        self._data = None
        self._expire_at = None

        self._edited = False

    @property
    def data(self):
        if not self._is_loaded():
            self._load_session()

        return self._data

    @property
    def key(self):
        if not self._is_loaded():
            self._load_session()

        return self._key

    @property
    def expire_at(self):
        if not self._is_loaded():
            self._load_session()

        return self._expire_at

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self._edited = True

    def need_save(self):
        return self._edited

    def _is_loaded(self):
        # key and expire_at may be None after load
        # so check data here
        return self._data is not None

    def _load_session(self):
        raw_data = self.engine.load(self.request)

        if raw_data:
            self._key = raw_data['key']
            self._data = raw_data['data']
            self._expire_at = raw_data['expire_at']
        else:
            self._data = {}


class BaseSessionStore:
    def __init__(self, app):
        self.app = app

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

    def set(self, key, data, expire_at):
        raise NotImplementedError


class SimpleSessionStore(BaseSessionStore):
    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)

        self.data = {}

    def get(self, key):
        return self.data.get(key, None)

    def set(self, key, data, expire_at):
        self.data[key] = {
            'key': key,
            'data': data,
            'expire_at': expire_at
        }


class SessionEngine:
    COOKIE_NAME = 'sessionid'
    EXPIRE_DAYS = 7

    def __init__(self, app):
        self.app = app
        self._store = None

    def flush(self, session, response):
        if session.need_save():
            expire_at = session.expire_at
            if expire_at is None:
                expire_at = get_now() + self.get_expire_length()

            key = session.key
            if key is None:
                key = random_string(length=32)

                name = self.cookie_name
                response.cookies[name] = key
                morsel = response.cookies[name]
                morsel['expires'] = format_datetime(expire_at, usegmt=True)
                morsel['path'] = '/'
                morsel['httponly'] = True

            self.store.set(key, session.data, expire_at)

    def load(self, request):
        cookie_name = self.cookie_name
        session_key = request.cookie.get(cookie_name, None)

        if session_key:
            store_data = self.store.get(session_key)
            if store_data is None:
                return

            for attr in ['key', 'expire_at', 'data']:
                if attr not in store_data:
                    return

            if store_data['key'] != session_key:
                return

            if not self.verify_data(store_data):
                return

            return store_data

    def verify_data(self, data):
        if data['expire_at'] < get_now():
            return False

        return True

    @property
    def cookie_name(self):
        return self.COOKIE_NAME

    @property
    def store(self):
        if self._store is None:
            cls = self.app.config.get(
                'session_store_class',
                SimpleSessionStore
            )
            self._store = cls(self.app)

        return self._store

    def get_expire_length(self):
        return datetime.timedelta(days=self.EXPIRE_DAYS)


async def session_middleware(controller, get_response):
    app = controller.app

    if not hasattr(app, 'session_engine'):
        app.session_engine = SessionEngine(app)

    request = controller.request
    request.session = Session(request, app.session_engine)

    response = await get_response(controller)
    app.session_engine.flush(request.session, response)

    return response
