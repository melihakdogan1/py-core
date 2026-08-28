"""1 GB sentetik web log dosyası üreten yardımcı script."""

import os
import random
import time
from pathlib import Path

IP_POOL = [f"192.168.1.{i}" for i in range(1, 255)] + [
    f"10.0.0.{i}" for i in range(1, 100)
]
METHODS = ["GET", "POST", "PUT", "DELETE"]
ENDPOINTS = [
    "/api/v1/users",
    "/api/v1/products",
    "/api/v1/orders",
    "/login",
    "/logout",
    "/checkout",
    "/static/bundle.js",
    "/healthz",
]
STATUS_CODES = [200, 200, 200, 201, 204, 400, 401, 403, 404, 500, 502]


def generate_log_file(target_path: Path, target_size_mb: int = 1024) -> None:
    target_bytes = target_size_mb * 1024 * 1024
    target_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Sentetik log üretiliyor ({target_size_mb} MB) -> {target_path}...")
    start_time = time.perf_counter()

    written_bytes = 0
    buffer: list[str] = []
    buffer_size = 50_000

    with open(target_path, "w", encoding="utf-8") as f:
        while written_bytes < target_bytes:
            ip = random.choice(IP_POOL)
            method = random.choice(METHODS)
            endpoint = random.choice(ENDPOINTS)
            status = random.choice(STATUS_CODES)
            response_size = random.randint(100, 15000)

            line = (
                f"{ip} - - [27/Aug/2026:12:00:00 +0000] "
                f'"{method} {endpoint} HTTP/1.1" {status} {response_size}\n'
            )
            buffer.append(line)

            if len(buffer) >= buffer_size:
                content = "".join(buffer)
                f.write(content)
                written_bytes += len(content.encode("utf-8"))
                buffer.clear()
                progress_mb = written_bytes / (1024 * 1024)
                print(
                    f"İlerleme: {progress_mb:.1f} MB / {target_size_mb} MB",
                    end="\r",
                )

        if buffer:
            content = "".join(buffer)
            f.write(content)
            written_bytes += len(content.encode("utf-8"))

    elapsed = time.perf_counter() - start_time
    file_size_mb = os.path.getsize(target_path) / (1024 * 1024)
    print(f"\nTamamlandı! Boyut: {file_size_mb:.2f} MB | Süre: {elapsed:.2f} sn")


if __name__ == "__main__":
    generate_log_file(Path("data/access.log"), target_size_mb=1024)
