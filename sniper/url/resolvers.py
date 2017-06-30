from collections import namedtuple
from itertools import chain

from . import patterns
from ..utils import merge_dict
from .actions import Action, ActionType

ResolveResult = namedtuple(
    'ResolveResult',
    ['controller', 'argv', 'kwargs'],
)


class UrlResolver:
    def __init__(self, pattern, controller=None, children=None, data=None):
        self.pattern = pattern
        self.controller = controller
        self.children = children
        self.data = data or {}

    def resolve(self, params):
        pattern_resolve_result = self.pattern.resolve(params)
        if not pattern_resolve_result:
            return

        kwargs = merge_dict(pattern_resolve_result.kwargs, self.data)

        if not self.children:
            return ResolveResult(
                controller=self.controller,
                argv=pattern_resolve_result.argv,
                kwargs=kwargs,
            )

        for child in self.children:
            new_params = params.copy()
            child_result = child.resolve(new_params)
            if child_result:
                if child_result.controller:
                    controller = child_result.controller
                else:
                    controller = self.controller

                return ResolveResult(
                    controller=controller,
                    argv=pattern_resolve_result.argv + child_result.argv,
                    kwargs=merge_dict(kwargs, child_result.kwargs)
                )


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


def include(regexp, children, controller=None, data=None):
    return UrlResolver(
        pattern=patterns.PathRegexpPattern(regexp),
        controller=controller,
        children=children,
        data=data
    )


def url(regexp, controller=None, method=None, data=None):
    if method:
        return include(regexp, [verb(method, controller, data=data)])

    return resolver(patterns.PathRegexpPattern(regexp), controller, data=data)


def verb(method, controller=None, data=None):
    return resolver(patterns.MethodPattern(method), controller, data=data)


def _build_default_actions():
    LIST_METHOD_ACTIONS = (
        ('GET', '', 'list'),
        ('POST', '', 'create'),
        ('GET', 'new', 'new'),
    )
    DETAIL_METHOD_ACTIONS = (
        ('GET', '', 'retrieve'),
        ('PUT', '', 'update'),
        ('PATCH', '', 'partial_update'),
        ('DELETE', '', 'destroy'),
        ('GET', 'edit', 'edit'),
        ('POST', 'update', 'update'),
        ('POST', 'destroy', 'destroy'),
    )

    return tuple(chain(
        (
            Action(
                type=ActionType.collection,
                method=method,
                path=path,
                action=action
            )
            for method, path, action in LIST_METHOD_ACTIONS
        ),
        (
            Action(
                type=ActionType.detail,
                method=method,
                path=path,
                action=action,
            )
            for method, path, action in DETAIL_METHOD_ACTIONS
        )
    ))


DEFAULT_ACTIONS = _build_default_actions()


def resource(name, controller, actions=[], children=[]):
    list_action_urls = []
    detail_action_urls = []

    for action in chain(DEFAULT_ACTIONS, actions):
        if action.path:
            regexp = r'^/%s$' % action.path
        else:
            regexp = r'^$'

        _url = url(
            regexp,
            method=action.method,
            data={'action': action.action}
        )

        if action.type == ActionType.collection:
            list_action_urls.append(_url)
        elif action.type == ActionType.detail:
            detail_action_urls.append(_url)

    base_path = '/' + name
    return include(
        r'^/' + name,
        [
            # list actions
            *list_action_urls,
            # detail actions
            include(
                r'^/(?P<pk>\w+)',
                detail_action_urls
            ),
        ],
        controller=controller,
        data={'resource_base_path': base_path}
    )


def method_actions(methods=None):
    if methods is None:
        methods = ['GET', 'POST']

    return [
        verb(m, data={'action': m.lower()})
        for m in methods
    ]
