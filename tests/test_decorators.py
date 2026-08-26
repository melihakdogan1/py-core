import pytest

from pycore.decorators import (
    TransactionManager,
    count_calls,
    managed_resource,
    memoize,
    retry,
    suppress_exceptions,
    temporary_attribute,
    timer_context,
    timing_decorator,
    validate_types,
)


def test_timing_decorator() -> None:
    @timing_decorator
    def slow_add(a: int, b: int) -> int:
        return a + b

    assert slow_add(2, 3) == 5
    assert hasattr(slow_add, "last_execution_time")


def test_retry_decorator() -> None:
    attempts = 0

    @retry(max_attempts=3, delay=0.001)
    def flaky_func() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Failed")
        return "Success"

    assert flaky_func() == "Success"
    assert attempts == 3


def test_retry_failure() -> None:
    @retry(max_attempts=2, delay=0.001)
    def always_fail() -> None:
        raise RuntimeError("Fatal")

    with pytest.raises(RuntimeError):
        always_fail()


def test_memoize() -> None:
    calls = 0

    @memoize
    def compute(x: int) -> int:
        nonlocal calls
        calls += 1
        return x * x

    assert compute(4) == 16
    assert compute(4) == 16
    assert calls == 1


def test_count_calls() -> None:
    @count_calls
    def greet(name: str) -> str:
        return f"Hi {name}"

    greet("A")
    greet("B")
    assert greet.calls == 2  # type: ignore[attr-defined]


def test_validate_types() -> None:
    @validate_types(int, str)
    def process(age: int, name: str) -> str:
        return f"{name}: {age}"

    assert process(25, "Melih") == "Melih: 25"
    with pytest.raises(TypeError):
        process("invalid", "Melih")  # type: ignore[arg-type]


def test_temporary_attribute() -> None:
    class Config:
        env = "production"

    cfg = Config()
    with temporary_attribute(cfg, "env", "test"):
        assert cfg.env == "test"
    assert cfg.env == "production"


def test_timer_context() -> None:
    with timer_context() as t:
        _ = sum(range(10000))
    assert t["elapsed"] > 0


def test_suppress_exceptions() -> None:
    with suppress_exceptions(ZeroDivisionError):
        _ = 1 / 0
    assert True


def test_transaction_manager() -> None:
    tx = TransactionManager()
    with tx:
        pass
    assert tx.committed is True
    assert tx.rolled_back is False

    tx_fail = TransactionManager()
    with tx_fail:
        raise ValueError("Error")
    assert tx_fail.committed is False
    assert tx_fail.rolled_back is True


def test_managed_resource() -> None:
    with managed_resource("DB") as res:
        assert res == "Resource<DB>"
