import asyncio
from dataclasses import dataclass
import random
import time
from typing import Any

import httpx
import requests

BASE_URL = "https://jsonplaceholder.typicode.com/posts"
TOTAL_REQUESTS = 200  # Halka açık API'yi yormamak ve rate-limit'e takılmamak için 200 istek (1000 için parametrik)


@dataclass
class BenchmarkResult:
    method: str
    total_time: float
    successful_requests: int
    failed_requests: int
    req_per_sec: float


# ==========================================
# (a) Senkron Requests (Blocking)
# ==========================================
def fetch_sync(total: int) -> BenchmarkResult:
    print(f"[Sync] {total} istek senkron olarak gönderiliyor...")
    start_time = time.perf_counter()
    success = 0
    failed = 0

    with requests.Session() as session:
        for i in range(1, total + 1):
            url = f"{BASE_URL}/{(i % 100) + 1}"
            try:
                resp = session.get(url, timeout=5.0)
                if resp.status_code == 200:
                    success += 1
                else:
                    failed += 1
            except Exception:
                failed += 1

    duration = time.perf_counter() - start_time
    return BenchmarkResult(
        method="Senkron (requests)",
        total_time=duration,
        successful_requests=success,
        failed_requests=failed,
        req_per_sec=total / duration if duration > 0 else 0,
    )


# ==========================================
# (b) Asenkron HTTPX + Semaphore + Retry
# ==========================================
async def fetch_with_retry(
    client: httpx.AsyncClient,
    url: str,
    semaphore: asyncio.Semaphore,
    max_retries: int = 3,
    base_backoff: float = 0.5,
) -> dict[str, Any] | None:
    async with semaphore:
        for attempt in range(max_retries):
            try:
                resp = await client.get(url, timeout=5.0)

                # 429 Too Many Requests (Rate Limit) veya 5xx Server Error yönetimi
                if resp.status_code == 429 or resp.status_code >= 500:
                    backoff = (base_backoff * (2**attempt)) + random.uniform(
                        0, 0.2
                    )
                    await asyncio.sleep(backoff)
                    continue

                resp.raise_for_status()
                return resp.json()  # type: ignore[no-any-return]

            except (httpx.RequestError, httpx.HTTPStatusError):
                if attempt == max_retries - 1:
                    return None
                backoff = (base_backoff * (2**attempt)) + random.uniform(0, 0.2)
                await asyncio.sleep(backoff)

        return None


async def fetch_async(total: int, concurrency_limit: int = 10) -> BenchmarkResult:
    print(
        f"[Async] {total} istek eşzamanlı (Semaphore={concurrency_limit}) gönderiliyor..."
    )
    start_time = time.perf_counter()
    semaphore = asyncio.Semaphore(concurrency_limit)
    limits = httpx.Limits(
        max_keepalive_connections=concurrency_limit,
        max_connections=concurrency_limit * 2,
    )

    async with httpx.AsyncClient(limits=limits) as client:
        tasks = [
            fetch_with_retry(
                client=client,
                url=f"{BASE_URL}/{(i % 100) + 1}",
                semaphore=semaphore,
            )
            for i in range(1, total + 1)
        ]
        results = await asyncio.gather(*tasks)

    duration = time.perf_counter() - start_time
    success = sum(1 for r in results if r is not None)
    failed = total - success

    return BenchmarkResult(
        method=f"Async (httpx + Semaphore({concurrency_limit}))",
        total_time=duration,
        successful_requests=success,
        failed_requests=failed,
        req_per_sec=total / duration if duration > 0 else 0,
    )


def main() -> None:
    print("--- Ödev 2.4: Senkron vs Asenkron API İstemcisi Benchmarkı ---\n")

    # 1. Senkron Test
    sync_res = fetch_sync(TOTAL_REQUESTS)
    print(
        f"  -> Bitti: {sync_res.total_time:.2f} sn ({sync_res.req_per_sec:.1f} req/s)\n"
    )

    # 2. Asenkron Test
    async_res = asyncio.run(fetch_async(TOTAL_REQUESTS, concurrency_limit=10))
    print(
        f"  -> Bitti: {async_res.total_time:.2f} sn ({async_res.req_per_sec:.1f} req/s)\n"
    )

    # Karşılaştırma Tablosu
    print("=" * 75)
    print(
        f"{'Yöntem':<35} | {'Süre (sn)':<10} | {'Başarılı':<10} | {'İstek/sn'}"
    )
    print("-" * 75)
    for res in [sync_res, async_res]:
        print(
            f"{res.method:<35} | {res.total_time:<10.2f} | {res.successful_requests:<10} | {res.req_per_sec:.1f}"
        )
    print("=" * 75)

    speedup = sync_res.total_time / async_res.total_time
    print(f"\nAsenkron İstemci Hızlandırma Oranı: ~{speedup:.1f}x kat daha hızlı!")


if __name__ == "__main__":
    main()