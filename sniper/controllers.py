import json

from . import middlewares
from .responses import Response
from .sessions import session_middleware


class BaseController:
    def __init__(self, request, *argv, **kwargs):
        self.request = request
        self.argv = argv
        self.kwargs = kwargs

        self.app = request.app

    def run(self):
        raise NotImplementedError


class Controller(BaseController):
    MIDDLEWARES = [
        middlewares.catch_http_errors,
        session_middleware,
        middlewares.ret_to_response,
        middlewares.handler_by_action,
    ]
    _middleware_entry = None   # lazy build

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)

        self.action = self.kwargs.get('action', 'handle')

    async def run(self):
        handler = self._get_middleware_entry()
        return await handler(self)

    def create_response(self, ret):
        return Response(ret)

    @classmethod
    def _get_middleware_entry(cls):
        if cls._middleware_entry is None:
            cls._middleware_entry = middlewares.build_entry(
                cls.MIDDLEWARES
            )

        return cls._middleware_entry


class NotFoundController(Controller):
    def run(self):
        return Response(
            'Not Found: %s %s\n' % (
                self.request.method,
                self.request.url.path
            ),
            status_code=404,
        )


class JsonResponseMixin:
    def create_response(self, ret):
        return Response(
            json.dumps(ret),
            headers=[
                ('Content-Type', 'application/json'),
            ]
        )


class JsonController(JsonResponseMixin, Controller):
    pass


class MethodActionsMixin:
    def get(self):
        return self.handle()

    def post(self):
        return self.handle()
