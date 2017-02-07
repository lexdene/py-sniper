from enum import Enum


class BaseAction:
    pass


class ResourceAction(BaseAction):
    ActionType = Enum('ActionType', ['collection', 'detail'], module=__name__)

    def __init__(self, type):
        self.type = type

    def get(self, action):
        pass

    def post(self, action):
        pass


collection = ResourceAction(ResourceAction.ActionType.collection)
detail = ResourceAction(ResourceAction.ActionType.detail)
