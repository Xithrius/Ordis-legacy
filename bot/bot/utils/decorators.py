import asyncio
from collections.abc import Callable, Coroutine
from typing import Any


def to_async(func: Callable[..., Any]) -> Callable[..., Coroutine[Any, Any, Any]]:  # pragma: no cover
    async def wrapper(*args, **kwargs) -> Any:
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper
