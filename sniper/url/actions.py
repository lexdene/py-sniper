from collections import namedtuple
from enum import Enum

ActionType = Enum('ActionType', ['collection', 'detail'], module=__name__)
Action = namedtuple(
    'Action',
    ['type', 'method', 'path'],
    module=__name__,
)


class ResourceActionCreator:

    def __init__(self, type):
        self.type = type

    def __getattr__(self, method):
        def create_action(path):
            return Action(
                type=self.type,
                method=method.upper(),
                path=path,
            )
        return create_action


collection = ResourceActionCreator(ActionType.collection)
detail = ResourceActionCreator(ActionType.detail)
