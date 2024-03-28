import asyncio
import functools
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import anyio
import pytest

from asyncur.aio import gather, run_async, start_tasks, wait_for, bulk_gather


def test_run_async():
    async def foo(sth: Any = ""):
        return sth

    assert run_async(foo) == ""
    assert run_async(foo()) == ""
    assert run_async(foo(1)) == 1
    assert run_async(foo(None)) is None
    assert run_async(foo(foo)) == foo
    assert run_async(functools.partial(foo, 2)) == 2


@pytest.mark.anyio
async def test_wait_for():
    async def do_sth(seconds=0.2):
        await anyio.sleep(seconds)
        return seconds

    assert (await wait_for(do_sth(), 1)) == 0.2
    with pytest.raises(TimeoutError):
        await wait_for(do_sth(), 0.1)


class TestGather:
    @pytest.mark.anyio
    async def test_gather(self):
        async def a():
            return 1

        async def b():
            return "2"

        async def c():
            pass

        assert (await gather(a(), b(), c())) == (1, "2", None)

    @staticmethod
    async def raise_error_later(seconds, err_type):
        await anyio.sleep(seconds)
        raise err_type(f"{seconds = }")

    @staticmethod
    def is_the_same_error(e1, e2):
        return type(e1) == type(e2) and str(e1) == str(e2)

    def create_coros_for_raise(self):
        coro1 = self.raise_error_later(0.2, ValueError)
        coro2 = self.raise_error_later(0.1, AttributeError)
        coro3 = self.raise_error_later(0.11, OSError)
        return coro1, coro2, coro3

    @pytest.mark.anyio
    async def test_gather_raise(self):
        err_asyncio = err_anyio = None
        try:
            await asyncio.gather(*self.create_coros_for_raise())
        except Exception as e:
            err_asyncio = e
        try:
            await gather(*self.create_coros_for_raise())
        except Exception as e:
            err_anyio = e
        assert self.is_the_same_error(err_asyncio, err_anyio)

    @pytest.mark.anyio
    async def test_gather_without_raise(self):
        results = await bulk_gather(self.create_coros_for_raise(), raises=False)
        assert results == (None, None, None)


class TestStartTasks:
    root = anyio.Path(__file__).parent
    names = ("tmp.txt", "tmp2.txt", "tmp3.txt")

    async def remove_files(self):
        for name in self.names:
            if await (p := self.root / name).exists():
                await p.unlink()

    async def startup(self):
        await self.root.joinpath(self.names[0]).touch()
        await anyio.sleep(1)
        await self.root.joinpath(self.names[1]).touch()

    async def running(self):
        while True:
            now = datetime.now()
            await self.root.joinpath(self.names[2]).write_text(str(now))
            await anyio.sleep(0.5)

    @pytest.mark.anyio
    async def test_start_tasks(self):
        await self.remove_files()
        root, names = self.root, self.names

        @asynccontextmanager
        async def lifespan(app):
            now = datetime.now()
            async with start_tasks(self.startup, self.running):
                await anyio.sleep(0.1)
                assert await root.joinpath(names[0]).exists()
                assert not (await root.joinpath(names[1]).exists())
                assert await root.joinpath(names[2]).exists()
                await anyio.sleep(1)
                assert await root.joinpath(names[0]).exists()
                assert await root.joinpath(names[1]).exists()
                assert (await root.joinpath(names[2]).read_text()) > str(now)
                yield
            now = datetime.now()
            assert (await root.joinpath(names[2]).read_text()) <= str(now)
            await self.remove_files()

        async with lifespan(None):
            for name in names:
                assert await root.joinpath(name).exists()

        for name in names:
            assert not await root.joinpath(name).exists()
