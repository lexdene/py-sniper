# url

## simple url

    from sniper.url import url

    urls = [
        url(r'^/$', hello_world),
    ]

## url with method

    from sniper.url import url

    urls = [
        url(r'^/$', hello_world, method='POST'),
    ]

now, `hello_world` can only be visited by POST request.

## include sub urls

    from sniper.url import url, include

    sub_urls = [
        url(r'^/hello$', hello_world),
    ]
    urls = [
        url(r'^/test', include(sub_urls)
    ]

the path for `hello_world` will be `/test/hello`.

## urls with path data

    from sniper.responses import Response
    from sniper.url import url

    def user(request, name):
        return Response('user name is %s\n' % name)

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
