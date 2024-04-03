from __future__ import annotations

import functools
import inspect
import time
from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    contextmanager,
)
from types import TracebackType
from typing import Any, Awaitable, Callable, Generator, TypeVar

T = TypeVar("T")


class Timer(AbstractContextManager, AbstractAsyncContextManager):
    """Print time cost of the function.

    Usage::
        >>> @Timer
        >>> async def main():
        ...     # ... async code or sync code ...

        >>> @Timer
        >>> def read_text(filename):
        ...     return Path(filename).read_text()

        >>> with Timer('do sth ...'):
        ...     # ... sync code ...

        >>> async with Timer('do sth ...'):
        ...     # ... async code ...
    """

    def __init__(self, message: str | Callable[..., T], decimal_places=1) -> None:
        func = None
        if callable(message):  # Use as decorator
            func = message
            self.__name__ = message = func.__name__
        self.message = message
        self.func = func
        self.decimal_places = decimal_places
        self.end = self.start = time.time()

    def _echo(self) -> None:
        self.end = self.echo_cost(self.start, self.decimal_places, self.message)

    @staticmethod
    def echo_cost(start: float, decimal_places: int, message: str) -> float:
        end = time.time()
        cost = end - start
        if decimal_places is not None:
            cost = round(cost, decimal_places)
        print(message, "Cost:", cost, "seconds")
        return end

    async def __aenter__(self) -> "Timer":
        return self.__enter__()

    async def __aexit__(self, *args, **kwargs) -> None:
        self.__exit__(*args, **kwargs)

    def __enter__(self) -> "Timer":
        self.start = time.time()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._echo()

    def _recreate_cm(self) -> "Timer":
        return self.__class__(self.func or self.message, self.decimal_places)

    def __call__(self, *args, **kwargs) -> None | T:
        if self.func is None:
            return None
        if inspect.iscoroutinefunction(self.func):

            @functools.wraps(self.func)
            async def inner(*args, **kwds):
                async with self._recreate_cm():
                    return await self.func(*args, **kwargs)

            return inner(*args, **kwargs)
        else:
            with self._recreate_cm():
                return self.func(*args, **kwargs)


@contextmanager
def timer(message: str, decimal_places=1) -> Generator[None, None, None]:
    """Print time cost of the function.

    Usage::
        >>> @timer('message')
        >>> def read_text(filename):
        ...     return Path(filename).read_text()

        >>> with timer('do sth ...'):
        ...     # ... sync code ...
    """
    start = time.time()
    try:
        yield
    finally:
        Timer.echo_cost(start, decimal_places, message)


FnT = TypeVar("FnT", Awaitable[Any], Any)


def timeit(func: Callable[..., FnT]) -> Callable[..., FnT]:
    """Print time cost of the function.

    Usage::
        >>> @timeit
        >>> async def main():
        ...     # ... async code ...

        >>> @timeit
        >>> def read_text(filename):
        ...     return Path(filename).read_text()

        >>> res = timeit(sync_func)(*args, **kwargs)
        >>> result = await timeit(async_func)(*args, **kwargs)
    """
    func_name = getattr(func, "__name__", str(func))
    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def deco(*args, **kwargs) -> Any:
            async with Timer(func_name):
                return await func(*args, **kwargs)

    else:

        @functools.wraps(func)
        def deco(*args, **kwargs) -> Any:
            with Timer(func_name):
                return func(*args, **kwargs)

    return deco
