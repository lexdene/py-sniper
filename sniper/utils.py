def cached_property(func):
    return _CachedProperty(func)


class _CachedProperty:
    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self

        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


def merge_dict(*args):
    result = dict()
    for arg in args:
        result.update(arg)

    return result


class QueryList:
    def __init__(self, data):
        assert isinstance(data, list), 'data must be list'
        self._data = data

    def get(self, name, default=None):
        for key, value in self._data:
            if key == name:
                return value

        return default

    def getlist(self, name):
        return [
            value
            for key, value in self._data
            if key == name
        ]

    def items(self):
        return iter(self._data)
