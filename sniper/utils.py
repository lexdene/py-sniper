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
