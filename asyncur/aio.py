import sys
from contextlib import asynccontextmanager
from typing import Any, Callable, Coroutine, Sequence

import anyio

if sys.version_info < (3, 11):
    from exceptiongroup import ExceptionGroup  # pragma: no cover


def ensure_afunc(coro: Coroutine | Callable) -> Callable:
    """Wrap coroutine to be async function"""
    if callable(coro):
        return coro

    async def do_await():
        return await coro

    return do_await


def run_async(coro: Coroutine | Callable) -> Any:
    """Compare with anyio.run and asyncio.run

    Usage::
        >>> async def afunc(n=1):
        ...     return n
        ...
        >>> run_async(afunc)  # get the same result as: await afunc()
        1
        >>> run_async(afunc(2))  # get the same result as: await afunc(2)
        2
    """
    return anyio.run(ensure_afunc(coro))


async def gather(*coros: Coroutine) -> tuple:
    """Similar like asyncio.gather"""
    return await bulk_gather(coros)


async def bulk_gather(
    coros: Sequence[Coroutine], bulk=0, use_semaphore=True, raises=True
) -> tuple:
    """Similar like asyncio.gather, if bulk is not zero, running tasks will limit to {bulk} every moment.

    :param coros: Coroutines
    :param bulk: running tasks limit number, set 0 to be unlimit
    :param use_semaphore: if True, use anyio.Semaphore to limit task number, else use multi task groups
    :param raises: if True, raise Exception when coroutine failed, else return None
    """
    total = len(coros)
    results = [None] * total

    async def runner(coro, i) -> None:
        results[i] = await coro

    async def limited_runner(coro, i, sema) -> None:
        async with sema:
            results[i] = await coro

    try:
        if bulk:
            if use_semaphore:
                semaphore = anyio.Semaphore(bulk)
                async with anyio.create_task_group() as tg:
                    async with semaphore:
                        for i, coro in enumerate(coros):
                            tg.start_soon(limited_runner, coro, i, semaphore)
            else:
                for start in range(0, total, bulk):
                    async with anyio.create_task_group() as tg:
                        for index, coro in enumerate(coros[start : start + bulk]):
                            tg.start_soon(runner, coro, start + index)
        else:
            async with anyio.create_task_group() as tg:
                for i, coro in enumerate(coros):
                    tg.start_soon(runner, coro, i)
    except ExceptionGroup as e:
        if raises:
            raise e.exceptions[0]

    return tuple(results)


@asynccontextmanager
async def start_tasks(coro: Coroutine | Callable, *more: Coroutine | Callable):
    """Make it easy to convert asyncio.create_task

    Usage:

    .. code-block:: python3

        async def startup():
            # cost a long time to do sth async
            await anyio.sleep(1000)

        @contextlib.asynccontextmanager
        async def lifespan(app):
            async with start_tasks(startup()):
                yield
    """
    async with anyio.create_task_group() as tg:
        with anyio.CancelScope(shield=True):
            tg.start_soon(ensure_afunc(coro))
            for c in more:
                tg.start_soon(ensure_afunc(c))
            try:
                yield
            finally:
                tg.cancel_scope.cancel()


async def wait_for(coro: Coroutine, timeout: int | float) -> Any:
    """Similar like asyncio.wait_for"""
    with anyio.fail_after(timeout):
        return await coro
