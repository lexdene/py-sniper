import random
import string


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

    def set(self, name, value):
        for index, line in enumerate(self._data):
            k, v = line

            if k == name:
                self._data[index] = (name, value)
                return

        self._data.append((name, value))

    def getlist(self, name):
        return [
            value
            for key, value in self._data
            if key == name
        ]

    def items(self):
        return iter(self._data)

    def copy(self):
        return self.__class__(list(self._data))


_DEFAULT_ALLOWED_CHARS = string.ascii_lowercase + string.digits


def random_string(allowed_chars=_DEFAULT_ALLOWED_CHARS, length=32):
    return ''.join(random.choice(allowed_chars) for _ in range(length))
