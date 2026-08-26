import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable, Coroutine
from typing import Any, TypeVar

T = TypeVar("T")


async def async_add(a: int, b: int, delay: float = 0.001) -> int:
    """Asenkron toplama ve simüle gecikme."""
    await asyncio.sleep(delay)
    return a + b


async def fetch_all_gather(
    coros: list[Coroutine[Any, Any, T]],
) -> list[T]:
    """asyncio.gather ile paralel görev çalıştırma."""
    return await asyncio.gather(*coros)


async def fetch_with_timeout(coro: Awaitable[T], timeout_sec: float) -> T | None:
    """Zaman aşımı korumalı asenkron çalıştırma."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_sec)
    except asyncio.TimeoutError:
        return None


async def rate_limited_fetch(
    urls: list[str],
    fetch_func: Callable[[str], Awaitable[dict[str, Any]]],
    concurrency_limit: int = 5,
) -> list[dict[str, Any]]:
    """asyncio.Semaphore ile rate limit kontrollü paralel istek yürütme."""
    semaphore = asyncio.Semaphore(concurrency_limit)

    async def sem_task(url: str) -> dict[str, Any]:
        async with semaphore:
            return await fetch_func(url)

    tasks = [sem_task(url) for url in urls]
    return await asyncio.gather(*tasks)


async def async_stream_generator(limit: int) -> AsyncIterator[int]:
    """Asenkron generator (async for) örneği."""
    for i in range(limit):
        await asyncio.sleep(0.001)
        yield i


async def retry_async(
    coro_func: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    delay: float = 0.001,
) -> T:
    """Asenkron exponential backoff retry mekanizması."""
    curr_delay = delay
    for attempt in range(1, max_retries + 1):
        try:
            return await coro_func()
        except Exception:
            if attempt == max_retries:
                raise
            await asyncio.sleep(curr_delay)
            curr_delay *= 2
    raise RuntimeError("Unreachable")


async def producer_consumer_queue(
    items: list[int],
) -> list[int]:
    """asyncio.Queue tabanlı üretici-tüketici deseni."""
    queue: asyncio.Queue[int | None] = asyncio.Queue()
    results: list[int] = []

    async def producer() -> None:
        for item in items:
            await queue.put(item)
        await queue.put(None)  # Sentinel

    async def consumer() -> None:
        while True:
            val = await queue.get()
            if val is None:
                queue.task_done()
                break
            results.append(val * 2)
            queue.task_done()

    await asyncio.gather(producer(), consumer())
    return results


async def race_first_completed(
    coros: list[Coroutine[Any, Any, T]],
) -> T:
    """İlk tamamlanan coroutine'in sonucunu döner."""
    tasks = [asyncio.create_task(c) for c in coros]
    done, pending = await asyncio.wait(
        tasks, return_when=asyncio.FIRST_COMPLETED
    )
    for p in pending:
        p.cancel()
    first_task = done.pop()
    return await first_task
