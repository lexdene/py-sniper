import asyncio

from .exceptions import HttpError
from .responses import Response


async def handler_by_action(controller, get_response):
    handler = getattr(controller, controller.action)
    result = handler()

    if asyncio.iscoroutine(result):
        result = await result

    return result


async def ret_to_response(controller, get_response):
    ret = await get_response(controller)

    if not isinstance(ret, Response):
        ret = controller.create_response(ret)

        if asyncio.iscoroutine(ret):
            ret = await ret

    return ret


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


def _build_entry_by_iter(it):
    try:
        func = next(it)
    except StopIteration:
        return None

    get_response = _build_entry_by_iter(it)

    async def entry(controller):
        return await func(
            controller,
            get_response
        )

    return entry
