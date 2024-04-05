__all__ = [
    "MIN_VALUE",
    "MAX_VALUE",
    "DOT_NOTATION_DELIMITER",
    "DOT_NOTATION_REGEX_PATTERN",
    "IEEE_NOTATION_DELIMITER",
    "IEEE_NOTATION_REGEX_PATTERN",
    "IETF_NOTATION_DELIMITER",
    "IETF_NOTATION_REGEX_PATTERN",
    "MACAddress",
    "parse_string",
    "to_hex_string",
    "to_dot_notation",
    "to_ieee_notation",
    "to_ietf_notation",
    "MACAddressValueError",
]

import re
import typing

MIN_VALUE: typing.Final[int] = int("0" * 12, base=16)
MAX_VALUE: typing.Final[int] = int("f" * 12, base=16)

DOT_NOTATION_DELIMITER: typing.Final[str] = "."
DOT_NOTATION_REGEX_PATTERN: typing.Final[
    re.Pattern[str]
] = re.compile(r"^[0-9a-f]{4}(\.[0-9a-f]{4}){2}$", re.I)

IEEE_NOTATION_DELIMITER: typing.Final[str] = "-"
IEEE_NOTATION_REGEX_PATTERN: typing.Final[
    re.Pattern[str]
] = re.compile(r"^[0-9a-f]{2}(-[0-9a-f]{2}){5}$", re.I)

IETF_NOTATION_DELIMITER: typing.Final[str] = ":"
IETF_NOTATION_REGEX_PATTERN: typing.Final[
    re.Pattern[str]
] = re.compile(r"^[0-9a-f]{2}(:[0-9a-f]{2}){5}$", re.I)


class MACAddress:
    __slots__ = ("_value",)

    def __init__(self, value: int, /) -> None:
        if value < MIN_VALUE:
            raise MACAddressValueError(f"{value} < {MIN_VALUE}")
        if value > MAX_VALUE:
            raise MACAddressValueError(f"{value} > {MAX_VALUE}")
        self._value = value

    def __str__(self) -> str:
        return hex(self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({to_ietf_notation(self)})"

    def __index__(self) -> int:
        return self._value

    def __hash__(self) -> int:
        return hash((type(self), self._value))

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, MACAddress):
            return self._value == other._value
        return NotImplemented

    def __lt__(self, other: typing.Any) -> bool:
        if isinstance(other, MACAddress):
            return self._value < other._value
        return NotImplemented

    def __le__(self, other: typing.Any) -> bool:
        if isinstance(other, MACAddress):
            return self._value <= other._value
        return NotImplemented

    def __gt__(self, other: typing.Any) -> bool:
        if isinstance(other, MACAddress):
            return self._value > other._value
        return NotImplemented

    def __ge__(self, other: typing.Any) -> bool:
        if isinstance(other, MACAddress):
            return self._value >= other._value
        return NotImplemented


def parse_string(value: str, /) -> MACAddress:
    if DOT_NOTATION_REGEX_PATTERN.fullmatch(value):
        value = value.replace(DOT_NOTATION_DELIMITER, "")
    elif IEEE_NOTATION_REGEX_PATTERN.fullmatch(value):
        value = value.replace(IEEE_NOTATION_DELIMITER, "")
    elif IETF_NOTATION_REGEX_PATTERN.fullmatch(value):
        value = value.replace(IETF_NOTATION_DELIMITER, "")
    try:
        return MACAddress(int(value, 16))
    except MACAddressValueError as exc:
        raise MACAddressValueError(value) from exc


def to_hex_string(
    address: MACAddress, 
    with_prefix: bool = True,
    with_padding: bool = False,
) -> str:
    hex_str = format(int(address), "x" if not with_padding else "0>12x")
    return ("0x" if with_prefix else "") + hex_str


def to_dot_notation(address: MACAddress) -> str:
    hex_str = to_hex_string(address, False, True)
    octet_quads = [hex_str[i:i + 4] for i in range(0, len(hex_str), 4)]
    return DOT_NOTATION_DELIMITER.join(octet_quads)


def to_ieee_notation(address: MACAddress) -> str:
    hex_str = to_hex_string(address, False, True)
    octet_pairs = [hex_str[i:i + 2] for i in range(0, len(hex_str), 2)]
    return IEEE_NOTATION_DELIMITER.join(octet_pairs)


def to_ietf_notation(address: MACAddress) -> str:
    hex_str = to_hex_string(address, False, True)
    octet_pairs = [hex_str[i:i + 2] for i in range(0, len(hex_str), 2)]
    return IETF_NOTATION_DELIMITER.join(octet_pairs)


class MACAddressValueError(ValueError):
    pass
