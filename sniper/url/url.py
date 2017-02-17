from collections import namedtuple

from sniper.utils import merge_dict

from . import patterns
from .actions import ActionType


ResolveResult = namedtuple(
    'ResolveResult',
    ['controller', 'argv', 'kwargs'],
)


class BaseUrlResolver:
    def __init__(self, pattern, controller=None, children=None, data=None):
        self.pattern = pattern
        self.controller = controller
        self.children = children
        self.data = data

    def match(self, params):
        '''
        if not match, return None.
        if match, return a (controller_class, argv, kwargs) tuple
        '''
        pass


class UrlResolver(BaseUrlResolver):
    def match(self, params):
        match = self.pattern.match(params)
        if match:
            if self.data:
                kwargs = merge_dict(match.kwargs, self.data)
            else:
                kwargs = match.kwargs

            if self.controller:
                return ResolveResult(
                    controller=self.controller,
                    argv=match.argv,
                    kwargs=kwargs,
                )
            elif self.children:
                new_params = merge_dict(params, match.new_params)

                for resolver in self.children:
                    child_match = resolver.match(new_params)
                    if child_match:
                        return ResolveResult(
                            controller=child_match.controller,
                            argv=match.argv + child_match.argv,
                            kwargs=merge_dict(kwargs, child_match.kwargs)
                        )


def include(children):
    # todo: support namespace
    return tuple(children)


def resolver(pattern, controller, data):
    if isinstance(controller, (tuple, list)):
        return UrlResolver(
            pattern=pattern,
            controller=None,
            children=controller,
            data=data,
        )
    else:
        return UrlResolver(
            pattern=pattern,
            controller=controller,
            children=None,
            data=data,
        )


def url(regexp, controller, method=None, data=None):
    if method:
        return url(regexp, include([verb(method, controller, data=data)]))

    return resolver(patterns.PathRegexpPattern(regexp), controller, data=data)


def verb(method, controller, data=None):
    # a better name for this function?
    return resolver(patterns.MethodPattern(method), controller, data=data)


def resource(name, controller, actions=[], children=[]):
    LIST_METHOD_ACTIONS = (
        ('GET', 'list'),
        ('POST', 'create'),
    )
    DETAIL_METHOD_ACTIONS = (
        ('GET', 'retrieve'),
        ('PUT', 'update'),
        ('PATCH', 'partial_update'),
        ('DELETE', 'destroy'),
    )

    list_action_urls = []
    detail_action_urls = []

    for action in actions:
        _url = url(
            r'^/%s$' % action.path,
            controller,
            method=action.method,
            data={'action': action.path}
        )

        if action.type == ActionType.collection:
            list_action_urls.append(_url)
        elif action.type == ActionType.detail:
            detail_action_urls.append(_url)

    return url(
        r'^/' + name,
        include([
            # list
            url(
                r'^$',
                include(
                    verb(method, controller, data={'action': action})
                    for method, action in LIST_METHOD_ACTIONS
                )
            ),
            # list actions
            *list_action_urls,
            # detail
            url(
                r'^/(?P<pk>\w+)$',
                include(
                    verb(method, controller, data={'action': action})
                    for method, action in DETAIL_METHOD_ACTIONS
                )
            ),
            # detail actions
            url(
                r'^/(?P<pk>\w+)',
                include(detail_action_urls)
            ),
        ])
    )
