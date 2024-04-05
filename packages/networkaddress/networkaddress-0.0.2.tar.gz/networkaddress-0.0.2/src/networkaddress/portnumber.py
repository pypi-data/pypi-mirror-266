__all__ = [
    "MIN_VALUE",
    "MAX_VALUE",
    "PortNumber",
    "InvalidPortNumber",
]

import typing

MIN_VALUE: typing.Final[int] = 0
MAX_VALUE: typing.Final[int] = 65535


class PortNumber:
    __slots__ = ("_value",)

    def __init__(self, value: int, /) -> None:
        if value < MIN_VALUE:
            raise InvalidPortNumber(f"{value} < {MIN_VALUE}")
        if value > MAX_VALUE:
            raise InvalidPortNumber(f"{value} > {MAX_VALUE}")
        self._value = value

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._value})"

    def __index__(self) -> int:
        return self._value

    def __hash__(self) -> int:
        return hash((type(self), self._value))

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, PortNumber):
            return self._value == other._value
        return NotImplemented

    def __lt__(self, other: typing.Any) -> bool:
        if isinstance(other, PortNumber):
            return self._value < other._value
        return NotImplemented

    def __le__(self, other: typing.Any) -> bool:
        if isinstance(other, PortNumber):
            return self._value <= other._value
        return NotImplemented

    def __gt__(self, other: typing.Any) -> bool:
        if isinstance(other, PortNumber):
            return self._value > other._value
        return NotImplemented

    def __ge__(self, other: typing.Any) -> bool:
        if isinstance(other, PortNumber):
            return self._value >= other._value
        return NotImplemented


class InvalidPortNumber(ValueError):
    pass
