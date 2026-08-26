import csv
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


class InMemorySink:
    """Testler ve doğrulama için bellek içi hedef havuzu."""

    def __init__(self) -> None:
        self.written_records: list[dict[str, Any]] = []

    def write(self, record: dict[str, Any]) -> None:
        self.written_records.append(record)

    def close(self) -> None:
        pass


class CsvSink:
    """Kayıtları CSV dosyasına yazan hedef havuzu."""

    def __init__(
        self,
        filepath: str | Path,
        fieldnames: list[str],
        encoding: str = "utf-8",
    ) -> None:
        self.filepath = Path(filepath)
        self.fieldnames = fieldnames
        self.encoding = encoding
        self.file = open(self.filepath, "w", encoding=self.encoding, newline="")
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        self.writer.writeheader()

    def write(self, record: dict[str, Any]) -> None:
        filtered = {k: record.get(k, "") for k in self.fieldnames}
        self.writer.writerow(filtered)

    def close(self) -> None:
        if not self.file.closed:
            self.file.close()


class SqliteSink:
    """Kayıtları SQLite veritabanı tablosuna yazan hedef havuzu."""

    def __init__(
        self, db_path: str | Path, table_name: str, columns: dict[str, str]
    ) -> None:
        self.db_path = Path(db_path)
        self.table_name = table_name
        self.columns = columns
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self) -> None:
        cols_def = ", ".join(f"{col} {dtype}" for col, dtype in self.columns.items())
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {self.table_name} ({cols_def});"
        )
        self.conn.commit()

    def write(self, record: dict[str, Any]) -> None:
        keys = list(self.columns.keys())
        values = [record.get(k) for k in keys]
        placeholders = ", ".join(["?"] * len(keys))
        cols_str = ", ".join(keys)
        self.cursor.execute(
            f"INSERT INTO {self.table_name} ({cols_str}) VALUES ({placeholders});",
            values,
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()


class StdoutSink:
    """Kayıtları JSON formatında standart çıktıya (stdout) basan hedef."""

    def __init__(self) -> None:
        pass

    def write(self, record: dict[str, Any]) -> None:
        sys.stdout.write(json.dumps(record, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    def close(self) -> None:
        pass
