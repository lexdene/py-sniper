import asyncio
import json

from . import middlewares
from .exceptions import MethodNotAllowed, NotFound
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
    ]
    _middleware_entry = None   # lazy build

    response_class = Response

    async def run(self):
        handler = self._get_middleware_entry()
        return await handler(self)

    async def inner_run(self):
        action = self.kwargs.get('action')

        if action:
            try:
                handler = getattr(self, action)
            except AttributeError:
                raise MethodNotAllowed()
        else:
            handler = self.handle

        result = handler()

        if asyncio.iscoroutine(result):
            result = await result

        if not isinstance(result, Response):
            result = self.process_return_data(result)
            result = await self.create_response(result)

        return result

    def process_return_data(self, ret):
        return ret

    async def create_response(self, ret):
        return self.response_class(ret)

    @classmethod
    def get_middlewares(cls):
        return cls.MIDDLEWARES

    @classmethod
    def _get_middleware_entry(cls):
        if cls._middleware_entry is None:
            cls._middleware_entry = middlewares.build_entry(
                cls.get_middlewares()
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
    async def create_response(self, ret):
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


class ModelController(JsonResponseMixin, Controller):
    def get_model(self):
        return self.model_class(self.app)

    def get_pk(self):
        return int(self.kwargs['pk'])

    def retrieve(self):
        model = self.get_model()

        pk = self.get_pk()
        obj = model.get_object(pk)

        if obj is None:
            raise NotFound()

        if obj:
            return obj
