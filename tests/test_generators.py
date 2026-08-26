from pycore.generators import (
    cartesian_product,
    chunk_stream,
    cycle_elements,
    fibonacci_gen,
    flatten_stream,
    group_consecutive,
    infinite_counter,
    running_accumulate,
    sliding_window_pairs,
    take,
)


def test_infinite_counter() -> None:
    gen = infinite_counter(start=10, step=2)
    assert [next(gen) for _ in range(3)] == [10, 12, 14]


def test_take() -> None:
    data = [1, 2, 3, 4, 5]
    assert take(3, data) == [1, 2, 3]


def test_fibonacci_gen() -> None:
    fib = fibonacci_gen()
    assert take(7, fib) == [0, 1, 1, 2, 3, 5, 8]


def test_chunk_stream() -> None:
    data = range(10)
    chunks = list(chunk_stream(data, 3))
    assert chunks == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]


def test_flatten_stream() -> None:
    streams = [[1, 2], [3, 4], [5]]
    assert list(flatten_stream(streams)) == [1, 2, 3, 4, 5]


def test_cycle_elements() -> None:
    assert cycle_elements(["A", "B"], 5) == ["A", "B", "A", "B", "A"]
    assert cycle_elements([], 5) == []


def test_running_accumulate() -> None:
    assert running_accumulate([1, 2, 3, 4]) == [1, 3, 6, 10]


def test_cartesian_product() -> None:
    assert cartesian_product([1, 2], ["x", "y"]) == [
        (1, "x"),
        (1, "y"),
        (2, "x"),
        (2, "y"),
    ]


def test_group_consecutive() -> None:
    assert group_consecutive(["A", "A", "B", "C", "C", "C"]) == [
        ("A", 2),
        ("B", 1),
        ("C", 3),
    ]


def test_sliding_window_pairs() -> None:
    res = list(sliding_window_pairs([1, 2, 3, 4]))
    assert res == [(1, 2), (2, 3), (3, 4)]
