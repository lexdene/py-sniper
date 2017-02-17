# sniper

sniper is a Python asynchronous restful web framework base on asyncio.

[asyncio][] is a Python standard library new in Python 3.4 which provides infrastructure for writing concurrent code and asynchronous network servers.

## Prerequisites

sniper support Python >= 3.5.

sniper should run on any operating system, but it has been fully tested only on Linux.

## Installation

    pip install sniper

## Hello world

Here is a simple "Hello world" example web app for sniper:

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

[asyncio]: https://docs.python.org/3/library/asyncio.html "Python asyncio library"
