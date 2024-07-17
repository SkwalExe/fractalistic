from typing import Generic, TypeVar

T = TypeVar("T")


class Vec(Generic[T]):
    x: T
    y: T

    def __init__(self, x: T, y: T) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"Vec({self.x}, {self.y})"
