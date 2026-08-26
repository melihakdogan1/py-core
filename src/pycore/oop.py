from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class Vector2D:
    """Vektör matematiği ve dunder metotları uygulayan sınıf."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Vector2D({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2D):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2D":
        return Vector2D(self.x * scalar, self.y * scalar)


class BankAccount:
    """@property kapsülleme ve bakiye doğrulama örneği."""

    def __init__(self, initial_balance: float = 0.0) -> None:
        self._balance = 0.0
        self.balance = initial_balance

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        if value < 0:
            raise ValueError("Bakiye negatif olamaz.")
        self._balance = float(value)

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Yatırılan tutar pozitif olmalıdır.")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self._balance:
            raise ValueError("Yetersiz bakiye.")
        self._balance -= amount


class PipelineStep:
    """mini-etl mimarisinin temeli: >> (__rshift__) operatör kompozisyonu."""

    def __init__(self, func: Any) -> None:
        self.func = func

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)

    def __rshift__(self, other: "PipelineStep") -> "PipelineStep":
        def chained(data: Any) -> Any:
            return other(self(data))

        return PipelineStep(chained)


class CustomCollection:
    """__len__, __getitem__ ve __iter__ protokollerini uygulayan koleksiyon."""

    def __init__(self, items: list[Any]) -> None:
        self._items = list(items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> Any:
        return self._items[index]

    def __iter__(self) -> Any:
        return iter(self._items)


class Temperature:
    """classmethod ve staticmethod kullanım örneği."""

    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    @classmethod
    def from_fahrenheit(cls, fahrenheit: float) -> "Temperature":
        celsius = (fahrenheit - 32) * 5 / 9
        return cls(celsius)

    @staticmethod
    def is_freezing(celsius: float) -> bool:
        return celsius <= 0.0


@dataclass(slots=True, frozen=True)
class ImmutableUser:
    """Düşük bellek maliyetli ve değiştirilemez veri sınıfı."""

    id: int
    username: str
    email: str


class BaseSink(ABC):
    """Veri yazma arayüzü (Abstract Base Class)."""

    @abstractmethod
    def write(self, record: dict[str, Any]) -> None:
        pass


class InMemorySink(BaseSink):
    """Testler ve bellek içi depolama için somut Sink."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def write(self, record: dict[str, Any]) -> None:
        self.records.append(record)


class Matrix2x2:
    """__matmul__ (@ operatörü) ve determinant hesabı."""

    def __init__(self, a: float, b: float, c: float, d: float) -> None:
        self.data = [[a, b], [c, d]]

    def determinant(self) -> float:
        return self.data[0][0] * self.data[1][1] - self.data[0][1] * self.data[1][0]

    def __matmul__(self, other: "Matrix2x2") -> "Matrix2x2":
        a = self.data[0][0] * other.data[0][0] + self.data[0][1] * other.data[1][0]
        b = self.data[0][0] * other.data[0][1] + self.data[0][1] * other.data[1][1]
        c = self.data[1][0] * other.data[0][0] + self.data[1][1] * other.data[1][0]
        d = self.data[1][0] * other.data[0][1] + self.data[1][1] * other.data[1][1]
        return Matrix2x2(a, b, c, d)


class SingletonMeta(type):
    """Thread-safe olmayan basit Singleton Metaclass örneği."""

    _instances: dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AppConfig(metaclass=SingletonMeta):
    def __init__(self, env: str = "production") -> None:
        self.env = env


class Polynomial:
    """__str__ ve __call__ ile polinom hesabı (ax^2 + bx + c)."""

    def __init__(self, a: float, b: float, c: float) -> None:
        self.a = a
        self.b = b
        self.c = c

    def __call__(self, x: float) -> float:
        return self.a * (x**2) + self.b * x + self.c


class CountedInstances:
    """Sınıf seviyesinde sayaç tutan örnek."""

    instance_count = 0

    def __init__(self) -> None:
        CountedInstances.instance_count += 1


class ComparableItem:
    """__lt__ ve __eq__ ile zengin karşılaştırma."""

    def __init__(self, name: str, priority: int) -> None:
        self.name = name
        self.priority = priority

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, ComparableItem):
            return NotImplemented
        return self.priority < other.priority

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ComparableItem):
            return NotImplemented
        return self.priority == other.priority


class LazyProperty:
    """İlk erişimde hesaplanan ve önbelleğe alınan descriptor/özellik."""

    def __init__(self, func: Any) -> None:
        self.func = func
        self.attrname = func.__name__

    def __get__(self, instance: Any, owner: Any = None) -> Any:
        if instance is None:
            return self
        val = self.func(instance)
        instance.__dict__[self.attrname] = val
        return val


class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    @LazyProperty
    def area(self) -> float:
        import math

        return math.pi * (self.radius**2)
