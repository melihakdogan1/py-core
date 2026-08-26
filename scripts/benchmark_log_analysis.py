from collections import Counter
from collections.abc import Iterator
from multiprocessing import Pool, cpu_count
import os
from pathlib import Path
import time
import tracemalloc
from typing import Any

import polars as pl

LOG_PATH = Path("data/access.log")


# ==========================================
# (a) Naif Satır Döngüsü (Naive Loop)
# ==========================================
def run_naive(filepath: Path) -> dict[str, int]:
    endpoint_counts: dict[str, int] = {}
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            parts = line.split('"')
            if len(parts) > 1:
                req = parts[1].split()
                if len(req) > 1:
                    endpoint = req[1]
                    endpoint_counts[endpoint] = (
                        endpoint_counts.get(endpoint, 0) + 1
                    )
    return endpoint_counts


# ==========================================
# (b) Generator + Counter
# ==========================================
def log_endpoint_stream(filepath: Path) -> Iterator[str]:
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            try:
                start = line.index('"') + 1
                end = line.index('"', start)
                yield line[start:end].split()[1]
            except (ValueError, IndexError):
                continue


def run_generator_counter(filepath: Path) -> Counter[str]:
    return Counter(log_endpoint_stream(filepath))


# ==========================================
# (c) Multiprocessing (Chunking ile Paralel)
# ==========================================
def process_chunk(args: tuple[Path, int, int]) -> Counter[str]:
    filepath, start_byte, end_byte = args
    counts: Counter[str] = Counter()

    with open(filepath, "rb") as f:
        f.seek(start_byte)
        if start_byte != 0:
            f.readline()  # İlk yarım satırı atla

        while f.tell() < end_byte:
            line_bytes = f.readline()
            if not line_bytes:
                break
            try:
                line = line_bytes.decode("utf-8", errors="ignore")
                start = line.index('"') + 1
                end = line.index('"', start)
                endpoint = line[start:end].split()[1]
                counts[endpoint] += 1
            except (ValueError, IndexError):
                continue
    return counts


def run_multiprocessing(filepath: Path) -> Counter[str]:
    file_size = os.path.getsize(filepath)
    num_workers = cpu_count()
    chunk_size = file_size // num_workers

    chunks = []
    for i in range(num_workers):
        start = i * chunk_size
        end = file_size if i == num_workers - 1 else (i + 1) * chunk_size
        chunks.append((filepath, start, end))

    with Pool(num_workers) as pool:
        results = pool.map(process_chunk, chunks)

    total_counts: Counter[str] = Counter()
    for res in results:
        total_counts.update(res)
    return total_counts


# ==========================================
# (d) Polars (Lazy & Rust Engine)
# ==========================================
def run_polars(filepath: Path) -> dict[str, int]:
    # Regex ile request alanından endpoint çıkarma ve agregasyon
    df = (
        pl.scan_csv(
            filepath,
            has_header=False,
            separator=" ",
            infer_schema_length=0,
            truncate_ragged_lines=True,
        )
        .select(pl.col("column_7").alias("endpoint"))
        .group_by("endpoint")
        .len()
        .collect(streaming=True)
    )
    return dict(zip(df["endpoint"].to_list(), df["len"].to_list()))


# ==========================================
# Runner & Metrik Ölçüm
# ==========================================
def measure_method(
    name: str, func: Any, *args: Any
) -> tuple[str, float, float, int]:
    tracemalloc.start()
    start_time = time.perf_counter()

    result = func(*args)

    duration = time.perf_counter() - start_time
    _, peak_mem_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mem_mb = peak_mem_bytes / (1024 * 1024)
    total_records = (
        sum(result.values())
        if isinstance(result, (dict, Counter))
        else len(result)
    )
    return name, duration, peak_mem_mb, total_records


def main() -> None:
    if not LOG_PATH.exists():
        print(f"Hata: {LOG_PATH} bulunamadı!")
        return

    print("--- Ödev 2.3: Performans Benchmark Başlıyor (1 GB Log) ---\n")

    methods = [
        ("(a) Naif Satır Döngüsü", run_naive),
        ("(b) Generator + Counter", run_generator_counter),
        ("(c) Multiprocessing", run_multiprocessing),
        ("(d) Polars (Streaming)", run_polars),
    ]

    results = []
    for name, fn in methods:
        print(f"Çalıştırılıyor: {name}...")
        res = measure_method(name, fn, LOG_PATH)
        results.append(res)
        print(f"  -> Süre: {res[1]:.2f} sn | Tepe Bellek: {res[2]:.2f} MB\n")

    print("\n" + "=" * 65)
    print(
        f"{'Yöntem':<28} | {'Süre (sn)':<10} | {'Tepe RAM (MB)':<14} | {'Kayıt Sayısı'}"
    )
    print("-" * 65)
    for name, dur, ram, count in results:
        print(f"{name:<28} | {dur:<10.2f} | {ram:<14.2f} | {count}")
    print("=" * 65)


if __name__ == "__main__":
    main()