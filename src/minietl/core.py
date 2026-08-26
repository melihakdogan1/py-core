import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any, Generic, Protocol, TypeVar

T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
T = TypeVar("T")
U = TypeVar("U")


@dataclass(slots=True)
class PipelineMetrics:
    """ETL yürütme istatistiklerini tutan metrik sınıfı."""

    read_count: int = 0
    written_count: int = 0
    error_count: int = 0
    duration_seconds: float = 0.0


@dataclass(slots=True)
class DeadLetterRecord:
    """Hatalı kayıtları ve hata nedenini tutan sınıf."""

    raw_data: Any
    error_message: str
    stage_name: str
    timestamp: float = field(default_factory=time.time)


class Source(Protocol[T_co]):
    """Veri okuma protokolü."""

    def read(self) -> Iterator[T_co]: ...


class Sink(Protocol[T_contra]):
    """Veri yazma protokolü."""

    def write(self, record: T_contra) -> None: ...

    def close(self) -> None: ...


class Transform(Generic[T, U]):
    """`>>` ile zincirlenebilir dönüşüm taban sınıfı."""

    def __init__(
        self,
        func: Callable[[T], U | None],
        name: str = "Transform",
    ) -> None:
        self.func = func
        self.name = name

    def __call__(self, item: T) -> U | None:
        return self.func(item)

    def __rshift__(self, other: "Transform[U, Any]") -> "Transform[T, Any]":
        def chained(item: T) -> Any:
            intermediate = self(item)
            if intermediate is None:
                return None
            return other(intermediate)

        return Transform(chained, name=f"{self.name} >> {other.name}")


class Pipeline(Generic[T, U]):
    """Source, Transform ve Sink bileşenlerini bağlayan ETL yöneticisi."""

    def __init__(
        self,
        source: Source[T],
        transform: Transform[T, U] | None = None,
        sinks: list[Sink[U]] | None = None,
    ) -> None:
        self.source = source
        self.transform = transform
        self.sinks: list[Sink[U]] = sinks or []
        self.dead_letters: list[DeadLetterRecord] = []
        self.metrics = PipelineMetrics()

    def add_sink(self, sink: Sink[U]) -> "Pipeline[T, U]":
        self.sinks.append(sink)
        return self

    def run(self) -> PipelineMetrics:
        """Akışı tek tek kayıt bazında yürütür (generator streaming)."""
        start_time = time.perf_counter()
        self.metrics = PipelineMetrics()
        self.dead_letters.clear()

        try:
            for raw_record in self.source.read():
                self.metrics.read_count += 1
                try:
                    processed_record: Any = raw_record
                    if self.transform is not None:
                        processed_record = self.transform(raw_record)

                    if processed_record is None:
                        continue

                    for sink in self.sinks:
                        sink.write(processed_record)
                    self.metrics.written_count += 1

                except Exception as exc:
                    self.metrics.error_count += 1
                    self.dead_letters.append(
                        DeadLetterRecord(
                            raw_data=raw_record,
                            error_message=str(exc),
                            stage_name=(
                                self.transform.name if self.transform else "Direct"
                            ),
                        )
                    )
        finally:
            for sink in self.sinks:
                sink.close()
            self.metrics.duration_seconds = time.perf_counter() - start_time

        return self.metrics
