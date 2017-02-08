import re
from collections import namedtuple

from . import routers


UrlResolver = namedtuple(
    'UrlResolver',
    ['router', 'controller'],
    module=__name__,
)

def url(regexp, controller, method=None):
    if isinstance(regexp, str):
        regexp = re.compile(regexp)

    router = routers.PathRegexpRouter(regexp)

    if method:
        router &= routers.MethodRouter(method)

    return UrlResolver(router, controller)


def resource(regexp, controller, actions=[], children=[]):
    pass
