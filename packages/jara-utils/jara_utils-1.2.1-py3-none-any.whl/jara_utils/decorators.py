import inspect
import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

log = logging.getLogger(__name__)


def timeit(*args, **kwargs) -> Any:
    """A method decorator which can be applied on async and sync methods."""

    def _log_execution(start: float, name: Any | None, coro: Callable) -> None:
        total = time.time() - start
        if total >= kwargs.get('threshold', 0.5):  # pragma: no cover
            log.warning(f'{name if name else coro.__name__} finished after %.3f seconds' % total)  # noqa: G002

    def inner(coro: Callable) -> Callable:
        @wraps(coro)
        async def wrapped(*coro_args, **coro_kwargs) -> Any:
            name = kwargs.get('name')
            start = time.time()
            try:
                return await coro(*coro_args, **coro_kwargs)
            finally:
                _log_execution(start, name, coro)

        @wraps(coro)
        def timed(*coro_args, **coro_kwargs) -> Any:
            name = kwargs.get('name')
            start = time.time()

            try:
                return coro(*coro_args, **coro_kwargs)
            finally:
                _log_execution(start, name, coro)

        if inspect.iscoroutinefunction(coro):
            return wrapped
        return timed

    if args:
        return inner(*args)
    return inner
