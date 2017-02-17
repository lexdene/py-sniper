# sniper

sniper is a Python asynchronous restful web framework base on asyncio.

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

## Documentation

see [docs](http://py-sniper.readthedocs.io/)
