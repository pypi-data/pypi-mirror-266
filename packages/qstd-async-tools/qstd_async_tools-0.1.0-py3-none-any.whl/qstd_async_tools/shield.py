import asyncio
import functools
import typing

from .background import run_in_background


T = typing.TypeVar("T")


async def shield(coroutine: typing.Coroutine[typing.Any, typing.Any, T]) -> T:
    task = run_in_background(coroutine)
    return await asyncio.shield(task)


def shield_decorator(func: T) -> T:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await shield(func(*args, **kwargs))
    return wrapper
