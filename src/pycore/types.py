from collections.abc import Callable, Iterator, Sequence
from typing import Any, Generic, Literal, NewType, Protocol, TypedDict, TypeVar

T_co = TypeVar("T_co", covariant=True)
T = TypeVar("T")
U = TypeVar("U")
UserId = NewType("UserId", int)


class UserDict(TypedDict):
    id: int
    name: str
    email: str
    is_active: bool


StatusType = Literal["pending", "processing", "completed", "failed"]


class StreamableSource(Protocol[T_co]):
    """Duck typing / structural interface for Sources."""

    def stream(self) -> Iterator[T_co]: ...


class Result(Generic[T]):
    """Generic Result container pattern (Ok / Err)."""

    def __init__(
        self,
        value: T | None = None,
        error: str | None = None,
        is_success: bool = True,
    ) -> None:
        self.value = value
        self.error = error
        self.is_success = is_success

    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        return cls(value=value, is_success=True)

    @classmethod
    def err(cls, error: str) -> "Result[T]":
        return cls(error=error, is_success=False)


def parse_user_dict(raw: dict[str, Any]) -> UserDict:
    """Sözlüğü TypedDict formatına güvenli şekilde dönüştürür."""
    return UserDict(
        id=int(raw["id"]),
        name=str(raw["name"]),
        email=str(raw["email"]),
        is_active=bool(raw.get("is_active", True)),
    )


def validate_status(status: str) -> StatusType:
    """Literal tip doğrulaması yapar."""
    valid_statuses = {"pending", "processing", "completed", "failed"}
    if status not in valid_statuses:
        raise ValueError(f"Geçersiz durum: {status}")
    return status  # type: ignore[return-value]


def apply_transformation(items: list[T], transform_func: Callable[[T], U]) -> list[U]:
    """Generic tip güvenli dönüşüm fonksiyonu."""
    return [transform_func(item) for item in items]


def read_all_from_stream(source: StreamableSource[T]) -> list[T]:
    """Protocol üzerinden miras şartı olmadan akışı okur."""
    return list(source.stream())


def create_user_id(val: int) -> UserId:
    """NewType ile tip güvenli UserId üretir."""
    if val <= 0:
        raise ValueError("ID pozitif olmalıdır.")
    return UserId(val)


def get_first_element(seq: Sequence[T]) -> T | None:
    """Sequence protokolünü (list, tuple, str) kabul eden generic fonksiyon."""
    return seq[0] if seq else None


def safe_cast_int(val: Any) -> int | None:
    """Union / Optional dönüşüm örneği."""
    try:
        return int(val)
    except (ValueError, TypeError):
        return None
