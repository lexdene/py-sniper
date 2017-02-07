import re

from . import routers


class Url:
    def __init__(self, router, controller):
        self.router = router
        self.controller = controller


def url(regexp, controller, method=None):
    if isinstance(regexp, str):
        regexp = re.compile(regexp)

    router = routers.PathRegexpRouter(regexp)

    if method:
        router &= routers.MethodRouter(method)

    return Url(router, controller)


def resource(regexp, controller, actions=[], children=[]):
    pass
