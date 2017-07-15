from sniper.filters import Q


class BaseModel:
    def __init__(self, app):
        self.app = app

    def get_queryset(self):
        return []

    def get_object(self, pk):
        return None

    def get_list(self, filters=None):
        return []


class Model(BaseModel):
    def get_object(self, pk):
        objects = self.get_list(
            filters=[Q(pk=pk)]
        )
        if not objects:
            return None

        return objects[0]

    def get_list(self, filters=None):
        queryset = self.get_queryset()

        if filters:
            for f in filters:
                queryset = self.apply_filter(queryset, f)

        return queryset

    def apply_filter(self, queryset, query):
        if query.key == 'pk':
            return [i for i in queryset if i['id'] == query.value]

        return queryset
