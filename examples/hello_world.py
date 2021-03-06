from sniper.app import Application
from sniper.responses import Response
from sniper.url import url


def hello_world(request):
    return Response('Hello world!\n')


if __name__ == '__main__':
    app = Application(
        urls=[
            url(r'^/$', hello_world),
        ]
    )
    app.run(8888)
