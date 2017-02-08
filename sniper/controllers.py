class BaseController:
    def __init__(self, request, url_params):
        self.request = request
        self.url_params = url_params

    def run(self):
        raise NotImplementedError


class Controller(BaseController):
    pass


class NotFoundController(Controller):
    pass
