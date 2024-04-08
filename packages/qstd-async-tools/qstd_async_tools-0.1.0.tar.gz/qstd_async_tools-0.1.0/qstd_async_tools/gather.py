import asyncio
import typing

from .trace import add_trace_id, trace_id, get_trace_ids


async def _wrapper(coroutine: typing.Coroutine, trace_ids: typing.List[str]):
    if trace_ids:
        add_trace_id(trace_ids)
    with trace_id():
        return await coroutine


def gather(*coroutines: typing.Coroutine, loop=None, return_exceptions=False):
    trace_ids = get_trace_ids()
    return asyncio.gather(
        *[_wrapper(coroutine, trace_ids) for coroutine in coroutines],
        loop=loop,
        return_exceptions=return_exceptions
    )
