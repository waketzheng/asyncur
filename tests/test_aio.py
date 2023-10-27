import functools
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import anyio
import pytest

from asyncur.aio import gather, run_async, start_tasks, wait_for


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


@pytest.mark.anyio
async def test_gather():
    async def a():
        return 1

    async def b():
        return "2"

    async def c():
        pass

    assert (await gather(a(), b(), c())) == (1, "2", None)


@pytest.mark.anyio
async def test_start_tasks():
    root = anyio.Path(__file__).parent
    names = ("tmp.txt", "tmp2.txt", "tmp3.txt")

    async def remove_files():
        for name in names:
            if await (p := root / name).exists():
                await p.unlink()

    await remove_files()

    async def startup():
        await root.joinpath(names[0]).touch()
        await anyio.sleep(1)
        await root.joinpath(names[1]).touch()

    async def running():
        while True:
            now = datetime.now()
            await root.joinpath(names[2]).write_text(str(now))
            await anyio.sleep(0.5)

    @asynccontextmanager
    async def lifespan(app):
        now = datetime.now()
        async with start_tasks(startup, running):
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
        await remove_files()

    async with lifespan(None):
        assert await root.joinpath(names[0]).exists()
        assert await root.joinpath(names[1]).exists()
        assert await root.joinpath(names[2]).exists()

    assert not await root.joinpath(names[0]).exists()
    assert not await root.joinpath(names[1]).exists()
    assert not await root.joinpath(names[2]).exists()
