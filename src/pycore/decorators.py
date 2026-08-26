import functools
import time
from collections.abc import Callable, Generator, Iterator
from contextlib import contextmanager
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def timing_decorator(func: F) -> F:
    """Fonksiyonun çalışma süresini ölçen ve metadata'yı koruyan decorator."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        execution_time = time.perf_counter() - start
        wrapper.last_execution_time = execution_time  # type: ignore[attr-defined]
        return result

    wrapper.last_execution_time = 0.0  # type: ignore[attr-defined]
    return wrapper  # type: ignore[return-value]


def retry(max_attempts: int = 3, delay: float = 0.01) -> Callable[[F], F]:
    """Hata durumunda fonksiyonu exponential backoff ile tekrar deneyen decorator."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc
                    if attempt == max_attempts:
                        break
                    time.sleep(current_delay)
                    current_delay *= 2
            if last_exception:
                raise last_exception

        return wrapper  # type: ignore[return-value]

    return decorator


def memoize(func: F) -> F:
    """Argümanlara göre fonksiyon sonuçlarını önbelleğe alan decorator."""
    cache: dict[tuple[Any, ...], Any] = {}

    @functools.wraps(func)
    def wrapper(*args: Any) -> Any:
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result

    wrapper.cache = cache  # type: ignore[attr-defined]
    return wrapper  # type: ignore[return-value]


def count_calls(func: F) -> F:
    """Fonksiyonun kaç kez çağrıldığını sayan decorator."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        wrapper.calls += 1  # type: ignore[attr-defined]
        return func(*args, **kwargs)

    wrapper.calls = 0  # type: ignore[attr-defined]
    return wrapper  # type: ignore[return-value]


def validate_types(*expected_types: type) -> Callable[[F], F]:
    """Pozisyonel argümanların tiplerini çalışma zamanında doğrulayan decorator."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for arg, expected in zip(args, expected_types):
                if not isinstance(arg, expected):
                    raise TypeError(f"Expected {expected}, got {type(arg)}")
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


@contextmanager
def temporary_attribute(obj: Any, attr_name: str, temp_value: Any) -> Iterator[None]:
    """with bloğu boyunca bir nesnenin özniteliğini geçici olarak
    değiştiren context manager.
    """
    original_exists = hasattr(obj, attr_name)
    original_val = getattr(obj, attr_name, None)
    setattr(obj, attr_name, temp_value)
    try:
        yield
    finally:
        if original_exists:
            setattr(obj, attr_name, original_val)
        else:
            delattr(obj, attr_name)


@contextmanager
def timer_context() -> Generator[dict[str, float], None, None]:
    """with bloğunun çalışma süresini ölçen context manager."""
    timing_data: dict[str, float] = {"elapsed": 0.0}
    start = time.perf_counter()
    try:
        yield timing_data
    finally:
        timing_data["elapsed"] = time.perf_counter() - start


@contextmanager
def suppress_exceptions(*exception_types: type[BaseException]) -> Iterator[None]:
    """Belirtilen hata tiplerini yutan context manager."""
    try:
        yield
    except exception_types:
        pass


class TransactionManager:
    """Commit ve Rollback davranışını simüle eden sınıf tabanlı context manager."""

    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    def __enter__(self) -> "TransactionManager":
        self.committed = False
        self.rolled_back = False
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        if exc_type is not None:
            self.rolled_back = True
            return True  # Hatayı yut
        self.committed = True
        return False


@contextmanager
def managed_resource(name: str) -> Iterator[str]:
    """Kaynak tahsisini ve temizliğini garanti eden generator context manager."""
    resource = f"Resource<{name}>"
    try:
        yield resource
    finally:
        # Temizlik adımı
        pass
