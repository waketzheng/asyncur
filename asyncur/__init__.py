import importlib.metadata
from pathlib import Path

from asyncur.aio import gather, run_async, start_tasks, wait_for

__version__ = importlib.metadata.version(Path(__file__).parent.name)
__all__ = (
    "__version__",
    "run_async",
    "gather",
    "start_tasks",
    "wait_for",
)
