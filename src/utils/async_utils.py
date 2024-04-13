import asyncio
from typing import Any, Awaitable, Callable


def async_exec(func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> None:
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(func(*args, **kwargs))
    except RuntimeError as e:
        if str(e).startswith('There is no current event loop in thread'):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(func(*args, **kwargs))
            loop.close()
        else:
            raise
