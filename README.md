# asyncur
[![LatestVersionInPypi](https://img.shields.io/pypi/v/asyncur.svg?style=flat)](https://pypi.python.org/pypi/asyncur)
[![GithubActionResult](https://github.com/waketzheng/asyncur/workflows/ci/badge.svg)](https://github.com/waketzheng/asyncur/actions?query=workflow:ci)
[![Coverage](https://coveralls.io/repos/github/waketzheng/asyncur/badge.svg)](https://coveralls.io/github/waketzheng/asyncur)

Some async functions that using anyio

## Requirements

Python 3.11+

## Installation

<div class="termy">

```console
$ pip install "asyncur"
---> 100%
Successfully installed asyncur
```

## Usage

- Read Excel File
```py
>>> from asycur.xls import load_xls
>>> await load_xls('tests/demo.xlsx')
[{'Column1': 'row1-\\t%c', 'Column2\nMultiLines': 0, 'Column 3': 1, 4: ''}, {'Column1': 'r2c1\n00', 'Column2\nMultiLines': 'r2 c2', 'Column 3': 2, 4: ''}]
```
