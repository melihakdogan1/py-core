import pytest

from pycore.oop import (
    AppConfig,
    BankAccount,
    BaseSink,
    Circle,
    ComparableItem,
    CustomCollection,
    ImmutableUser,
    InMemorySink,
    Matrix2x2,
    PipelineStep,
    Polynomial,
    Temperature,
    Vector2D,
)


def test_vector_repr() -> None:
    v = Vector2D(1, 2)
    assert repr(v) == "Vector2D(1, 2)"


def test_vector_add_sub_mul() -> None:
    v1 = Vector2D(1, 2)
    v2 = Vector2D(3, 4)
    assert v1 + v2 == Vector2D(4, 6)
    assert v2 - v1 == Vector2D(2, 2)
    assert v1 * 3 == Vector2D(3, 6)


def test_bank_account_deposit_withdraw() -> None:
    acc = BankAccount(100)
    acc.deposit(50)
    acc.withdraw(30)
    assert acc.balance == 120


def test_bank_account_validation_errors() -> None:
    acc = BankAccount(100)
    with pytest.raises(ValueError):
        acc.balance = -10
    with pytest.raises(ValueError):
        acc.withdraw(500)


def test_pipeline_step_rshift_composition() -> None:
    step1 = PipelineStep(lambda x: x + 5)
    step2 = PipelineStep(lambda x: x * 2)
    pipeline = step1 >> step2
    assert pipeline(10) == 30


def test_custom_collection_len() -> None:
    c = CustomCollection([1, 2, 3, 4])
    assert len(c) == 4


def test_custom_collection_iter_getitem() -> None:
    c = CustomCollection([10, 20, 30])
    assert c[1] == 20
    assert list(c) == [10, 20, 30]


def test_temperature_from_fahrenheit() -> None:
    t = Temperature.from_fahrenheit(32)
    assert t.celsius == 0.0


def test_temperature_is_freezing() -> None:
    assert Temperature.is_freezing(-1.0) is True
    assert Temperature.is_freezing(5.0) is False


def test_immutable_user_dataclass() -> None:
    u = ImmutableUser(1, "melih", "melih@test.com")
    assert u.id == 1
    with pytest.raises(Exception):
        u.username = "changed"  # type: ignore[misc]


def test_abc_sink_implementation() -> None:
    sink = InMemorySink()
    assert isinstance(sink, BaseSink)
    sink.write({"id": 1})
    assert len(sink.records) == 1


def test_matrix_determinant_and_matmul() -> None:
    m1 = Matrix2x2(1, 2, 3, 4)
    m2 = Matrix2x2(2, 0, 1, 2)
    assert m1.determinant() == -2.0
    m3 = m1 @ m2
    assert m3.data == [[4, 4], [10, 8]]


def test_singleton_app_config() -> None:
    cfg1 = AppConfig("staging")
    cfg2 = AppConfig("prod")
    assert cfg1 is cfg2
    assert cfg2.env == "staging"


def test_polynomial_call() -> None:
    poly = Polynomial(2, 3, 1)  # 2x^2 + 3x + 1
    assert poly(2) == 15.0


def test_comparable_and_lazy_property() -> None:
    item1 = ComparableItem("Low", 1)
    item2 = ComparableItem("High", 10)
    assert item1 < item2

    c = Circle(2)
    assert round(c.area, 2) == 12.57
    assert "area" in c.__dict__  # cached
