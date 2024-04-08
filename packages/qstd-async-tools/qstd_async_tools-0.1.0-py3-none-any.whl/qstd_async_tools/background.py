import asyncio
import functools
import typing

from .trace import get_trace_ids, add_trace_id


BACKGROUND_TASKS = set()


async def _wrapper(
    coroutine: typing.Coroutine,
    trace_ids: typing.Union[typing.List[str], None]
):
    if trace_ids:
        add_trace_id(trace_ids)
    return await coroutine


def run_in_background(coroutine: typing.Coroutine):
    task = asyncio.create_task(_wrapper(coroutine, get_trace_ids()))

    BACKGROUND_TASKS.add(task)

    task.add_done_callback(BACKGROUND_TASKS.discard)
    return task


def run_in_background_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        run_in_background(func(*args, **kwargs))
    return wrapper
