from sniper.app import Application
from sniper.responses import Response
from sniper.url import url


def user(request, name):
    return Response('user name is %s\n' % name)


if __name__ == '__main__':
    app = Application(
        urls=[
            url(r'^/user/(?P<name>\w+)$', user)
        ]
    )
    app.run(8888)
