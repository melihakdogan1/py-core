import itertools
from collections.abc import Generator, Iterable, Iterator
from typing import Any, TypeVar

T = TypeVar("T")


def infinite_counter(start: int = 0, step: int = 1) -> Generator[int, None, None]:
    """Sonsuz sayı üreteci (itertools.count idiyomu)."""
    current = start
    while True:
        yield current
        current += step


def take(n: int, iterable: Iterable[T]) -> list[T]:
    """Bir iterable'dan ilk n elemanı çeker."""
    return list(itertools.islice(iterable, n))


def fibonacci_gen() -> Generator[int, None, None]:
    """Sonsuz Fibonacci serisi üretir."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def chunk_stream(
    iterable: Iterable[T], chunk_size: int
) -> Generator[list[T], None, None]:
    """Bir veri akışını belleğe yüklemeden n boyutlu parçalar halinde üretir."""
    iterator = iter(iterable)
    while True:
        chunk = list(itertools.islice(iterator, chunk_size))
        if not chunk:
            break
        yield chunk


def flatten_stream(iterable_of_iterables: Iterable[Iterable[T]]) -> Iterator[T]:
    """İç içe iterable akışlarını tek bir akışta birleştirir (itertools.chain)."""
    return itertools.chain.from_iterable(iterable_of_iterables)


def cycle_elements(elements: list[T], limit: int) -> list[T]:
    """Elemanları sonsuz döngüye sokup belirtilen limit kadarını listeler."""
    if not elements:
        return []
    return list(itertools.islice(itertools.cycle(elements), limit))


def running_accumulate(numbers: list[int]) -> list[int]:
    """Kümülatif toplam akışını döner (itertools.accumulate)."""
    return list(itertools.accumulate(numbers))


def cartesian_product(list_a: list[Any], list_b: list[Any]) -> list[tuple[Any, Any]]:
    """İki listenin kartezyen çarpımını döner."""
    return list(itertools.product(list_a, list_b))


def group_consecutive(elements: list[T]) -> list[tuple[T, int]]:
    """Ardışık aynı elemanları gruplayarak (eleman, adet) döner (itertools.groupby)."""
    return [(key, len(list(group))) for key, group in itertools.groupby(elements)]


def sliding_window_pairs(iterable: Iterable[T]) -> Iterator[tuple[T, T]]:
    """Akış üzerindeki ardışık ikilileri kaydırarak üretir (pairwise)."""
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)
