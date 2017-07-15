from collections import namedtuple

Query = namedtuple(
    'Query',
    ['key', 'value'],
)


def Q(*argv, **kwargs):
    if kwargs:
        argv = list(kwargs.items())[0]

    return Query(*argv)
