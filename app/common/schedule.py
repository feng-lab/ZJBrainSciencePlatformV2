import asyncio
import functools
import logging
from typing import Awaitable, Callable

Fn = Callable[[], None]
AsyncFn = Callable[[], Awaitable[None]]

logger = logging.getLogger(__name__)


def repeat_task(
    interval_in_seconds: float, max_repetitions: int | None = None
) -> Callable[[Fn | AsyncFn], AsyncFn]:
    def decorator(func: Fn | AsyncFn) -> AsyncFn:
        is_async_fn = asyncio.iscoroutinefunction(func)
        first_run = True

        @functools.wraps(func)
        async def wrapper() -> None:
            nonlocal first_run
            if not first_run:
                return
            first_run = False
            repetitions = 0

            async def loop() -> None:
                nonlocal repetitions
                while max_repetitions is None or repetitions < max_repetitions:
                    try:
                        if is_async_fn:
                            await func()
                        else:
                            await asyncio.to_thread(func)
                        repetitions += 1
                    except Exception as e:
                        logger.error(f"repeat task raise error: {e}")
                    await asyncio.sleep(interval_in_seconds)

            asyncio.create_task(loop())

        return wrapper

    return decorator
