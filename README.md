# asyncur
![Python Versions](https://img.shields.io/pypi/pyversions/asyncur)
[![LatestVersionInPypi](https://img.shields.io/pypi/v/asyncur.svg?style=flat)](https://pypi.python.org/pypi/asyncur)
[![GithubActionResult](https://github.com/waketzheng/asyncur/workflows/ci/badge.svg)](https://github.com/waketzheng/asyncur/actions?query=workflow:ci)
[![Coverage Status](https://coveralls.io/repos/github/waketzheng/asyncur/badge.svg?branch=main)](https://coveralls.io/github/waketzheng/asyncur?branch=main)
![Mypy coverage](https://img.shields.io/badge/mypy-100%25-green.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Some async functions that using anyio, and toolkit for excel read.

## Installation

<div class="termy">

```console
$ pip install asyncur
---> 100%
Successfully installed asyncur
```
Or use poetry:
```console
poetry add asyncur
```

## Usage

- bulk_gather/gather/run_async
```py
>>> from asyncur import gather, run_async
>>> async def foo():
...     return 1
...
>>> await bulk_gather([foo(), foo()])
(1, 1)
>>> await gather(foo(), foo())
(1, 1)
>>> run_async(gather(foo(), foo()))
(1, 1)
```
- timeit
```py
>>> import time
>>> import anyio
>>> from asyncur import timeit
>>> @timeit
... async def sleep_test():
...     await anyio.sleep(3)
...
>>> await sleep()
sleep_test Cost: 3.0 seconds

>>> @timeit
... def sleep_test2():
...     time.sleep(3.1)
...
>>> sleep_test2()
sleep_test2 Cost: 3.1 seconds
```

- Read Excel File(need to install with xls extra: `pip install "asyncur[xls]"`)
```py
>>> from asycur.xls import load_xls
>>> await load_xls('tests/demo.xlsx')
[{'Column1': 'row1-\\t%c', 'Column2\nMultiLines': 0, 'Column 3': 1, 4: ''}, {'Column1': 'r2c1\n00', 'Column2\nMultiLines': 'r2 c2', 'Column 3': 2, 4: ''}]
```
