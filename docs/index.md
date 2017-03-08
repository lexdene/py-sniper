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

## Contributing

Source code can be found on [Github][].

Feature requests, bug reports and other issues can be raised on the [GitHub issue tracker][].

Pull requests can be sent on the [Github pull requests][].

[asyncio]: https://docs.python.org/3/library/asyncio.html "Python asyncio library"
[Github]: https://github.com/lexdene/py-sniper "py-sniper on github"
[Github issue tracker]: https://github.com/lexdene/py-sniper/issues "issues of py-sniper"
[Github pull requests]: https://github.com/lexdene/py-sniper/pulls "pull requests of py-sniper"
