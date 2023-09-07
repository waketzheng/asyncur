from contextlib import asynccontextmanager
from typing import Callable, Coroutine

import anyio


def ensure_afunc(coro: Coroutine | Callable) -> Callable:
    if callable(coro):
        return coro

    async def do_await():
        return await coro

    return do_await


def run_async(coro: Coroutine | Callable):
    return anyio.run(ensure_afunc(coro))


async def gather(*coros):
    results = [None] * len(coros)

    async def runner(coro, i):
        results[i] = await coro

    async with anyio.create_task_group() as tg:
        for i, coro in enumerate(coros):
            tg.start_soon(runner, coro, i)

    return results


@asynccontextmanager
async def start_tasks(coro: Coroutine | Callable, *more: Coroutine | Callable):
    async with anyio.create_task_group() as tg:
        with anyio.CancelScope(shield=True):
            tg.start_soon(ensure_afunc(coro))
            for c in more:
                tg.start_soon(ensure_afunc(c))
            yield
            tg.cancel_scope.cancel()
