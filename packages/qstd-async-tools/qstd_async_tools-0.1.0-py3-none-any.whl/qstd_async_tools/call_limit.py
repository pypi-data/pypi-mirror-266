import asyncio
import functools
import typing


class CallQueue:
    current = 0
    maximum: int
    next: typing.List[asyncio.Future]

    def __init__(self, maximum: int):
        self.maximum = maximum
        self.next = []

    async def waiting(self):
        if self.current == self.maximum:
            future = asyncio.Future()
            self.next.append(future)
            await future
        else:
            self.current += 1

    def end(self):
        if len(self.next) != 0:
            self.next.pop(0).set_result(None)
        else:
            self.current -= 1


def call_limit(maximum: int):
    q = CallQueue(maximum)

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            await q.waiting()
            try:
                return await func(*args, **kwargs)
            finally:
                q.end()
        return wrapper
    return decorator

