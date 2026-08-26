import csv
import json
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any


class CsvSource:
    """Bellek dostu satır bazlı CSV okuyucu (generator streaming)."""

    def __init__(self, filepath: str | Path, encoding: str = "utf-8") -> None:
        self.filepath = Path(filepath)
        self.encoding = encoding

    def read(self) -> Iterator[dict[str, Any]]:
        with open(self.filepath, encoding=self.encoding, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield {k: v for k, v in row.items() if k is not None}


class JsonlSource:
    """Bellek dostu satır satır JSON (JSONL) okuyucu."""

    def __init__(self, filepath: str | Path, encoding: str = "utf-8") -> None:
        self.filepath = Path(filepath)
        self.encoding = encoding

    def read(self) -> Iterator[dict[str, Any]]:
        with open(self.filepath, encoding=self.encoding) as f:
            for line in f:
                line_stripped = line.strip()
                if line_stripped:
                    data = json.loads(line_stripped)
                    if isinstance(data, dict):
                        yield data


class HttpApiSource:
    """HTTP REST API üzerinden veri çeken streaming source (stdlib)."""

    def __init__(self, url: str, timeout: float = 10.0) -> None:
        self.url = url
        self.timeout = timeout

    def read(self) -> Iterator[dict[str, Any]]:
        req = urllib.request.Request(self.url, headers={"User-Agent": "MiniETL/0.1.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        yield item
            elif isinstance(data, dict):
                yield data
