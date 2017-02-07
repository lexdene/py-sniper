from enum import Enum


class BaseRouter:
    def match(self, request, params):
        '''
        test if current router match request

        if not match, return None.
        if match, return a tuple (argv, kwargs) which are the captured arguments.

        :param request: request object
        :param dict params: params during url match
        '''
        return None

    def __or__(self, other):
        return RouterCombination(
            relation=RouterCombination.OR,
            items=[self, other],
        )

    def __and__(self, other):
        return RouterCombination(
            relation=RouterCombination.AND,
            items=[self, other],
        )

    def __not__(self):
        return RouterCombination(
            relation=RouterCombination.NOT,
            items=[self],
        )


class RouterCombination(BaseRouter):
    Relation = Enum('Relation', ['OR', 'AND', 'NOT'], module=__name__)

    def __init__(self, relation, items):
        self.relation = relation
        self.items = items

    def match(self, request, params):
        if self.relation == Relation.NOT:
            return not self.items[0].match(request, params)

        if self.relation == Relation.AND:
            reduce_method = all
        elif self.relation == Relation.OR:
            reduce_method = any
        else:
            raise ValueError('no such relation: %s' % self.relation)

        return reduce_method(
            item.match(request, params)
            for item in self.items
        )


class PathRegexpRouter(BaseRouter):
    def __init__(self, regexp, children=None):
        self.regexp = regexp
        self.children = children or []

    def match(self, request, params):
        if 'path' in params:
            path = params['path']
        else:
            path = request.parsed_url.path

        match = self.regexp.match(path)

        if match:
            argv = []
            kwargs = match.groupdict()
            if not kwargs:
                argv = match.groups()

            path_tail = re.sub(self.regexp, '', path)

            if self.children:
                new_params = copy.copy(params)
                new_params['path'] = path_tail

                for child in self.children:
                    result = child.match(request, new_params)

                    if result:
                        argv += result[0]
                        kwargs.update(result[1])

                        return argv, kwargs

            else:
                if not path_tail:
                    return argv, kwargs


class MethodRouter(BaseRouter):
    def __init__(self, method):
        self.method = method

    def match(self, request, params):
        if self.method == request.method:
            return [], {}
