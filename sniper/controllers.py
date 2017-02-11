from sniper.responses import Response


class BaseController:
    def __init__(self, request, *argv, **kwargs):
        self.request = request
        self.argv = argv
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError


class Controller(BaseController):
    def get_handler_name(self):
        return self.kwargs['action']

    def to_response(self, result):
        return Response(result)

    def run(self):
        handler_name = self.get_handler_name()
        handler = getattr(self, handler_name)

        result = handler()

        response = self.to_response(result)
        return response


class NotFoundController(Controller):
    def run(self):
        return Response(
            'Not Found: %s %s\n' % (
                self.request.method,
                self.request.url.path
            ),
            status_code=404,
        )
