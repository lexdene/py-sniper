import re
from collections import namedtuple

PatternResolveResult = namedtuple(
    'PatternResolveResult',
    ['argv', 'kwargs'],
)


class BasePattern:
    def resolve(self, params):
        '''
            test if current pattern can resolve params

            if can resolve, return a PatternResolveResult object.
            otherwise, return None.

            :param dict params: params during resolve
        '''
        if self.match(params):
            return PatternResolveResult(
                argv=(),
                kwargs={},
            )

    def match(self, params):
        '''
            test if current pattern can match params.

            return boolean.
        '''
        return False


class PathRegexpPattern(BasePattern):
    def __init__(self, regexp):
        self.regexp = re.compile(regexp)

    def resolve(self, params):
        # params['path'] should be the tail part of previous pattern
        if 'path' in params:
            path = params['path']
        else:
            path = params['request'].url.path

        match = self.regexp.match(path)

        if match:
            argv = ()
            kwargs = match.groupdict()
            if not kwargs:
                argv = match.groups()

            # path is the tail part for next pattern
            params['path'] = path[match.end():]

            return PatternResolveResult(
                argv=argv,
                kwargs=kwargs,
            )


class MethodPattern(BasePattern):
    def __init__(self, method):
        self.method = method

    def match(self, params):
        request = params['request']

        return request.method == self.method


def resolve_patterns(pattern_list, params):
    argv = []
    kwargs = {}

    for pattern in pattern_list:
        result = pattern.resolve(params)
        if not result:
            return

        argv += result.argv
        kwargs.update(result.kwargs)

    return PatternResolveResult(
        argv=argv,
        kwargs=kwargs,
    )
