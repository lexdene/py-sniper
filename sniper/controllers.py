from . import middlewares
from .responses import Response


class BaseController:
    def __init__(self, request, *argv, **kwargs):
        self.request = request
        self.argv = argv
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError


class Controller(BaseController):
    MIDDLEWARES = [
        middlewares.catch_http_errors,
        middlewares.handler_by_action,
    ]
    _middleware_entry = None   # lazy build

    async def run(self):
        handler = self._get_middleware_entry()
        return await handler(self)

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
