import csv
import json
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
                # Boş satırları veya None değerleri temizle
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
