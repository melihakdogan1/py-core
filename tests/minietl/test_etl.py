import sqlite3
from pathlib import Path
from typing import Any

from hypothesis import given
from hypothesis import strategies as st

from minietl.core import Pipeline
from minietl.sinks import CsvSink, InMemorySink, SqliteSink
from minietl.sources import CsvSource, JsonlSource
from minietl.transforms import (
    cast_field,
    filter_record,
    map_record,
    rename_fields,
    validate_required_fields,
)


class DummySource:

    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.data = data

    def read(self) -> Any:
        for item in self.data:
            yield item


def test_pipeline_transform_composition() -> None:
    raw_data = [
        {"id": "1", "name": "melih", "score": "85"},
        {"id": "2", "name": "ali", "score": "40"},
        {"id": "3", "name": "can", "score": "not_a_number"},
    ]

    source = DummySource(raw_data)
    sink = InMemorySink()

    transform = (
        validate_required_fields({"id", "name", "score"})
        >> rename_fields({"name": "fullname"})
        >> cast_field("score", int)
        >> filter_record(lambda r: r["score"] > 50)
    )

    pipeline = Pipeline(source=source, transform=transform, sinks=[sink])
    metrics = pipeline.run()

    assert metrics.read_count == 3
    assert metrics.written_count == 1
    assert metrics.error_count == 1
    assert len(pipeline.dead_letters) == 1
    assert sink.written_records[0]["fullname"] == "melih"


def test_csv_and_jsonl_sources(tmp_path: Path) -> None:
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("id,val\n1,foo\n2,bar\n")
    csv_source = CsvSource(csv_file)
    csv_records = list(csv_source.read())
    assert len(csv_records) == 2
    assert csv_records[0]["val"] == "foo"

    jsonl_file = tmp_path / "test.jsonl"
    jsonl_file.write_text('{"id": 1, "val": "a"}\n{"id": 2, "val": "b"}\n')
    jsonl_source = JsonlSource(jsonl_file)
    jsonl_records = list(jsonl_source.read())
    assert len(jsonl_records) == 2
    assert jsonl_records[1]["val"] == "b"


def test_csv_and_sqlite_sinks(tmp_path: Path) -> None:
    data = [{"id": 101, "name": "Alpha"}, {"id": 102, "name": "Beta"}]

    csv_out = tmp_path / "out.csv"
    csv_sink = CsvSink(csv_out, fieldnames=["id", "name"])
    pipeline_csv = Pipeline(
        source=DummySource(data), transform=None, sinks=[csv_sink]
    )
    pipeline_csv.run()
    assert csv_out.exists()
    content = csv_out.read_text()
    assert "id,name" in content
    assert "101,Alpha" in content

    db_out = tmp_path / "test.db"
    sqlite_sink = SqliteSink(
        db_path=db_out,
        table_name="users",
        columns={"id": "INTEGER", "name": "TEXT"},
    )
    pipeline_sqlite = Pipeline(
        source=DummySource(data), transform=None, sinks=[sqlite_sink]
    )
    pipeline_sqlite.run()

    conn = sqlite3.connect(db_out)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM users ORDER BY id ASC;")
    rows = cursor.fetchall()
    conn.close()

    assert len(rows) == 2
    assert rows[0] == (101, "Alpha")


@given(st.integers(min_value=0, max_value=1000))
def test_hypothesis_pipeline_preserves_data(val: int) -> None:
    source = DummySource([{"num": str(val)}])
    sink = InMemorySink()

    transform = cast_field("num", int) >> map_record(
        lambda r: {"doubled": r["num"] * 2}
    )

    pipeline = Pipeline(source=source, transform=transform, sinks=[sink])
    pipeline.run()

    assert len(sink.written_records) == 1
    assert sink.written_records[0]["doubled"] == val * 2


@given(st.text(alphabet=st.characters(blacklist_categories=("Cs",))))
def test_hypothesis_rename_fields(field_val: str) -> None:
    source = DummySource([{"old_key": field_val}])
    sink = InMemorySink()

    transform = rename_fields({"old_key": "new_key"})
    pipeline = Pipeline(source=source, transform=transform, sinks=[sink])
    pipeline.run()

    assert "new_key" in sink.written_records[0]
    assert sink.written_records[0]["new_key"] == field_val


@given(st.lists(st.integers(), min_size=1, max_size=50))
def test_hypothesis_stream_item_count(items: list[int]) -> None:
    raw_items = [{"id": i} for i in items]
    source = DummySource(raw_items)
    sink = InMemorySink()

    pipeline = Pipeline(source=source, transform=None, sinks=[sink])
    metrics = pipeline.run()

    assert metrics.read_count == len(items)
    assert metrics.written_count == len(items)
    assert metrics.error_count == 0