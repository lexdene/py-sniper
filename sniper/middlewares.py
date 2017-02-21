import asyncio
import json

from .responses import Response


async def handler_by_action(controller, get_response):
    action = controller.kwargs['action']
    handler = getattr(controller, action)
    result = handler()

    if asyncio.iscoroutine(result):
        result = await result

    return result


async def body_to_response(controller, get_response):
    result = await get_response(controller)
    return Response(result)


async def json_data(controller, get_response):
    result = await get_response(controller)
    return Response(json.dumps(result))


def build_entry(mws):
    if not mws:
        return None

    async def entry(controller):
        i = iter(mws)
        m = next(i)

        return await m(controller, build_entry(list(i)))

    return entry
