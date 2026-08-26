import asyncio
from typing import Any

import pytest

from pycore.asyncs import (
    async_add,
    async_stream_generator,
    fetch_all_gather,
    fetch_with_timeout,
    producer_consumer_queue,
    race_first_completed,
    rate_limited_fetch,
    retry_async,
)


@pytest.mark.asyncio
async def test_async_add() -> None:
    res = await async_add(10, 20)
    assert res == 30


@pytest.mark.asyncio
async def test_fetch_all_gather() -> None:
    coros = [async_add(1, 1), async_add(2, 2), async_add(3, 3)]
    res = await fetch_all_gather(coros)
    assert res == [2, 4, 6]


@pytest.mark.asyncio
async def test_fetch_with_timeout() -> None:
    success = await fetch_with_timeout(async_add(1, 1, delay=0.001), 0.1)
    assert success == 2

    timeout_res = await fetch_with_timeout(async_add(1, 1, delay=0.1), 0.001)
    assert timeout_res is None


@pytest.mark.asyncio
async def test_rate_limited_fetch() -> None:
    async def mock_fetch(url: str) -> dict[str, Any]:
        await asyncio.sleep(0.001)
        return {"url": url, "status": 200}

    urls = ["http://api.test/1", "http://api.test/2", "http://api.test/3"]
    results = await rate_limited_fetch(urls, mock_fetch, concurrency_limit=2)
    assert len(results) == 3
    assert results[0]["status"] == 200


@pytest.mark.asyncio
async def test_async_stream_generator() -> None:
    res: list[int] = []
    async for num in async_stream_generator(4):
        res.append(num)
    assert res == [0, 1, 2, 3]


@pytest.mark.asyncio
async def test_retry_async_success() -> None:
    attempts = 0

    async def flaky() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ConnectionError("Flaky")
        return "OK"

    res = await retry_async(flaky, max_retries=3, delay=0.001)
    assert res == "OK"
    assert attempts == 2


@pytest.mark.asyncio
async def test_retry_async_failure() -> None:
    async def always_fail() -> None:
        raise ValueError("Fatal")

    with pytest.raises(ValueError):
        await retry_async(always_fail, max_retries=2, delay=0.001)


@pytest.mark.asyncio
async def test_producer_consumer_queue() -> None:
    res = await producer_consumer_queue([1, 2, 3])
    assert res == [2, 4, 6]


@pytest.mark.asyncio
async def test_race_first_completed() -> None:
    async def fast() -> str:
        await asyncio.sleep(0.001)
        return "fast"

    async def slow() -> str:
        await asyncio.sleep(0.1)
        return "slow"

    winner = await race_first_completed([fast(), slow()])
    assert winner == "fast"


@pytest.mark.asyncio
async def test_async_add_zero_delay() -> None:
    res = await async_add(0, 0, delay=0.0)
    assert res == 0
