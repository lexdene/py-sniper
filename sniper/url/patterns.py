import re
from collections import namedtuple


PatternMatchResult = namedtuple(
    'PatternMatchResult',
    ['argv', 'kwargs', 'new_params'],
)


class BasePattern:
    def match(self, params):
        '''
            test if current pattern match params

            if not match, return None.
            if match, return a PatternMatchResult object.

            :param dict params: params during match
        '''
        pass


class PathRegexpPattern(BasePattern):
    def __init__(self, regexp):
        self.regexp = re.compile(regexp)

    def match(self, params):
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

            new_params = dict(
                path=path[match.end():],
            )

            return PatternMatchResult(
                argv=argv,
                kwargs=kwargs,
                new_params=new_params
            )


class MethodPattern(BasePattern):
    def __init__(self, method):
        self.method = method

    def match(self, params):
        request = params['request']

        if request.method == self.method:
            return PatternMatchResult(
                argv=(),
                kwargs={},
                new_params={},
            )
