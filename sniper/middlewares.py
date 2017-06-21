from .exceptions import HttpError
from .responses import Response


async def catch_http_errors(controller, get_response):
    try:
        return await get_response(controller)
    except HttpError as e:
        return Response(
            body=e.detail,
            status_code=e.status_code
        )


def build_entry(middleware_list):
    return _build_entry_by_iter(iter(middleware_list))


async def default_get_response(controller):
    return await controller.inner_run()


def _build_entry_by_iter(it):
    try:
        func = next(it)
    except StopIteration:
        return None

    get_response = _build_entry_by_iter(it) or default_get_response

    async def entry(controller):
        r = await func(
            controller,
            get_response
        )
        assert isinstance(r, Response), \
            'middleware must return a response object'
        return r

    return entry
