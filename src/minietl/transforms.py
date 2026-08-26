from collections.abc import Callable
from typing import Any

from minietl.core import Transform


def map_record(
    fn: Callable[[dict[str, Any]], dict[str, Any]],
    name: str = "Map",
) -> Transform[dict[str, Any], dict[str, Any]]:
    """Kayıt üzerinde genel alan dönüşümü yapar."""
    return Transform(fn, name=name)


def filter_record(
    predicate: Callable[[dict[str, Any]], bool],
    name: str = "Filter",
) -> Transform[dict[str, Any], dict[str, Any]]:
    """Koşulu sağlamayan kayıtları filtreler (None döner)."""

    def apply(record: dict[str, Any]) -> dict[str, Any] | None:
        return record if predicate(record) else None

    return Transform(apply, name=name)


def rename_fields(
    mapping: dict[str, str],
    name: str = "Rename",
) -> Transform[dict[str, Any], dict[str, Any]]:
    """Sözlükteki alan isimlerini yeniden adlandırır."""

    def apply(record: dict[str, Any]) -> dict[str, Any]:
        return {mapping.get(k, k): v for k, v in record.items()}

    return Transform(apply, name=name)


def cast_field(
    field_name: str,
    target_type: type,
    name: str = "Cast",
) -> Transform[dict[str, Any], dict[str, Any]]:
    """Belirtilen alanı hedef veri tipine dönüştürür; hatalıysa exception fırlatır."""

    def apply(record: dict[str, Any]) -> dict[str, Any]:
        if field_name not in record or record[field_name] is None:
            return record
        copy_rec = dict(record)
        copy_rec[field_name] = target_type(copy_rec[field_name])
        return copy_rec

    return Transform(apply, name=f"{name}({field_name}->{target_type.__name__})")


def validate_required_fields(
    required_keys: set[str],
    name: str = "Validate",
) -> Transform[dict[str, Any], dict[str, Any]]:
    """Zorunlu alanların varlığını doğrular; eksikse ValueError fırlatır."""

    def apply(record: dict[str, Any]) -> dict[str, Any]:
        missing = required_keys - set(record.keys())
        if missing:
            raise ValueError(f"Eksik zorunlu alanlar: {sorted(missing)}")
        return record

    return Transform(apply, name=name)
