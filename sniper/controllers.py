from sniper.responses import Response


class BaseController:
    def __init__(self, request, *argv, **kwargs):
        self.request = request
        self.argv = argv
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError


class Controller(BaseController):
    pass


class NotFoundController(Controller):
    def run(self):
        return Response(
            'Not Found: %s %s\n' % (
                self.request.method,
                self.request.url.path
            ),
            status_code=404,
        )
