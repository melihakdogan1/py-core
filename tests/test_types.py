import pytest

from pycore.types import (
    Result,
    UserId,
    apply_transformation,
    create_user_id,
    get_first_element,
    parse_user_dict,
    read_all_from_stream,
    safe_cast_int,
    validate_status,
)


def test_typed_dict_parsing() -> None:
    raw = {"id": 1, "name": "Melih", "email": "melih@test.com"}
    user = parse_user_dict(raw)
    assert user["id"] == 1
    assert user["is_active"] is True


def test_status_literal_validation() -> None:
    assert validate_status("pending") == "pending"
    assert validate_status("completed") == "completed"
    with pytest.raises(ValueError):
        validate_status("unknown_status")


def test_generic_result_container() -> None:
    success = Result.ok(100)
    assert success.is_success is True
    assert success.value == 100

    failure = Result.err("Connection timeout")
    assert failure.is_success is False
    assert failure.error == "Connection timeout"


def test_generic_transformation() -> None:
    numbers = [1, 2, 3]
    strings = apply_transformation(numbers, lambda x: f"num_{x}")
    assert strings == ["num_1", "num_2", "num_3"]


def test_protocol_duck_typing() -> None:
    class DummyStream:
        def stream(self) -> list[int]:
            return [10, 20, 30]

    dummy = DummyStream()
    res = read_all_from_stream(dummy)  # type: ignore[arg-type]
    assert res == [10, 20, 30]


def test_newtype_user_id() -> None:
    uid = create_user_id(42)
    assert isinstance(uid, int)
    assert uid == UserId(42)
    with pytest.raises(ValueError):
        create_user_id(-5)


def test_sequence_protocol() -> None:
    assert get_first_element([10, 20]) == 10
    assert get_first_element(("a", "b")) == "a"
    assert get_first_element("") is None


def test_safe_cast_int() -> None:
    assert safe_cast_int("123") == 123
    assert safe_cast_int("abc") is None
    assert safe_cast_int(None) is None


def test_result_err_state() -> None:
    res = Result[int].err("Failed")
    assert res.value is None
    assert res.is_success is False


def test_typed_dict_keys() -> None:
    raw = {"id": 2, "name": "Test", "email": "t@t.com", "is_active": False}
    user = parse_user_dict(raw)
    assert user["is_active"] is False
