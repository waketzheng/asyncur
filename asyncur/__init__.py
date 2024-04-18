import importlib.metadata
from pathlib import Path

from asyncur.aio import gather, run, run_async, start_tasks, wait_for
from asyncur.timing import timeit
from asyncur.utils import AttrDict

__version__ = importlib.metadata.version(Path(__file__).parent.name)
__all__ = (
    "__version__",
    "AttrDict",
    "run",
    "run_async",
    "gather",
    "start_tasks",
    "timeit",
    "wait_for",
)
