sniper
======

|travis-status| |docs|

sniper is a Python asynchronous restful web framework base on asyncio.

Advantage
---------

* It is a very small framework
* It supports non-blocking, asynchronous web application development (thanks to Python's asyncio library) which has better performance in high concurrency situation
* It has no dependencies except Python itself

Hello world
-----------

Here is a simple "Hello world" example web app for sniper:

.. code-block:: python

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

Documentation
-------------

see `docs <http://py-sniper.readthedocs.io>`_

.. |travis-status| image:: https://travis-ci.org/lexdene/py-sniper.svg?branch=master
    :alt: travis status
    :target: https://travis-ci.org/lexdene/py-sniper

.. |docs| image:: https://readthedocs.org/projects/py-sniper/badge/?version=master
    :target: http://py-sniper.readthedocs.io/en/master/?badge=master
    :alt: Documentation Status
