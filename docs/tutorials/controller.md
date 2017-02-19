# Controller

## controller function

controller can be a function:

    from sniper.responses import Response

    def hello(request):
        return Response('hello world!')

Its first argument is request object.

## BaseController class

controller can be a class

    from sniper.controllers import BaseController
    from sniper.responses import Response

    class HelloCtrl(BaseController):
        def run(self):
            return Response('Hello world!')

The class must redefine `run` method.
You can get the request object from `self.request`.

## coroutine controller

controller function or the `run` method of controller class can be a coroutine function.

    async def hello(request):
        data = await some_coroutine_function()
        return Response('data is %s' % data)

    class HelloCtrl(BaseController):
        async def run(self):
            data = await some_coroutine_function()
            return Response('data is %s' % data)
