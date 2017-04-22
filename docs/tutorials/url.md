# url

## simple url

    from sniper.url import url

    urls = [
        url(r'^/$', hello_world),
    ]

Its first argument is a regexp pattern with match the path of request.

Its second argument is a controller function. see [Controller](controller).

## url with method

    from sniper.url import url

    urls = [
        url(r'^/$', hello_world, method='POST'),
    ]

now, `hello_world` can only be visited by POST request.

## urls with path data

    from sniper.responses import Response
    from sniper.url import url

    def user(request, name):
        return Response('user name is %s' % name)

    urls = [
        url(r'^/user/(?P<name>\w+)$', user)
    ]

visit `/user/Elephant`, you will get output: `user name is Elephant`.

## urls with specific data

    urls = [
        url(r'^/author$', user, data={'name': 'Elephant'])
    ]

name will be `Elephant` in user function.

Specific data has higher priority.

    urls = [
        url(r'^/user/(?P<name>\w+)$', user, data={'name': 'Elephant})
    ]

`name` param will always be `Elephant` no matter what url you visit if it matches `^/test/(?P<name>\w+)$` pattern.

## include sub urls

    from sniper.url import url, include

    sub_urls = [
        url(r'^/hello$', hello_world),
    ]
    urls = [
        include(r'^/test', sub_urls)
    ]

the path for `hello_world` will be `/test/hello`.

### specific controler when include sub urls

You can specific a controller when include sub urls and omit the controller param inside sub urls.

This is usefull when route multiple path to same controller with different data.

But if you also provide controller param inside sub urls, the inner one takes effect.

    sub_urls = [
        url(r'^/foo$', data={'action': 'foo'}),
        url(r'^/bar$', data={'action': 'bar'}),
        url(r'^/baz$', goodbye_world, data={'action': 'baz'}),
    ]
    urls = [
        include(r'^/hello', sub_urls, controller=hello_world),
    ]
