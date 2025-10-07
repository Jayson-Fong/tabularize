"""
Test cases for parsing.
"""

from typing import Iterable

import tabularize


def _parse(
    header_line: bytearray | bytes,
    body_lines: Iterable[bytearray | bytes],
    force: Iterable[bytearray | bytes] | None = None,
) -> list[dict[bytes, bytearray | bytes]]:
    headers: tuple[tuple[bytes, int, int | None], ...] = tabularize.parse_headers(
        header_line, force=force
    )

    body: list[dict[bytes, bytearray | bytes]] = []
    for body_line in body_lines:
        body.append(tabularize.parse_body(headers, body_line))

    return body


def test_basic():
    data: list[bytes] = (
        b"""
Apple  Banana  Carrot    Date  Elderberry  Fava
Fruit  Fruit   Vegetable Fruit Fruit     Vegetable""".strip().splitlines()
    )

    parsed: list[dict[bytes, bytes]] = _parse(data[0], data[1:])
    assert parsed == [
        {
            b"Apple": b"Fruit",
            b"Banana": b"Fruit",
            b"Carrot": b"Vegetable",
            b"Date": b"Fruit",
            b"Elderberry": b"Fruit",
            b"Fava": b"Vegetable",
        }
    ]


def test_force_header():
    data: list[bytes] = (
        b"""
Name Preference
Jane Candy""".strip().splitlines()
    )

    parsed: list[dict[bytes, bytes]] = _parse(data[0], data[1:])
    assert parsed == [{b"Name Preference": b"Jane Candy"}]

    parsed: list[dict[bytes, bytes]] = _parse(data[0], data[1:], force=(b"Name",))
    assert parsed == [{b"Name": b"Jane", b"Preference": b"Candy"}]


def test_tabbed():
    data: list[bytes] = (
        b"""
Name\tPreference
Jane\tCandy""".strip().splitlines()
    )

    parsed: list[dict[bytes, bytes]] = _parse(data[0], data[1:])
    assert parsed == [{b"Name": b"Jane", b"Preference": b"Candy"}]


def test_short_data():
    data: list[bytes] = (
        b"""
Name\tPreference
Jane""".strip().splitlines()
    )

    parsed: list[dict[bytes, bytes]] = _parse(data[0], data[1:])
    assert parsed == [{b"Name": b"Jane"}]


def test_end_header():
    data: list[bytes] = b"""Name\nJane""".strip().splitlines()

    parsed: list[dict[bytes, bytes]] = _parse(data[0], data[1:])
    assert parsed == [{b"Name": b"Jane"}]


def test_padded_end_header():
    data: list[bytes] = b"""Name \nJane""".strip().splitlines()

    parsed: list[dict[bytes, bytes]] = _parse(data[0], data[1:])
    assert parsed == [{b"Name": b"Jane"}]


def test_double_padded_end_header():
    data: list[bytes] = b"""Name \nJane""".strip().splitlines()

    parsed: list[dict[bytes, bytes]] = _parse(data[0], data[1:])
    assert parsed == [{b"Name": b"Jane"}]


def test_tabbed_end_header():
    data: list[bytes] = b"""Name\t\nJane""".strip().splitlines()

    parsed: list[dict[bytes, bytes]] = _parse(data[0], data[1:])
    assert parsed == [{b"Name": b"Jane"}]


def test_blank_header():
    data: list[bytes] = [b"\t", b"Jane"]

    parsed: list[dict[bytes, bytes]] = _parse(data[0], data[1:])
    assert parsed == [{}]


def test_lookback():
    data: list[bytes] = (
        b"""
Name    Preference
Jane   Ice Cream""".strip().splitlines()
    )

    parsed: list[dict[bytes, bytes]] = _parse(data[0], data[1:])
    assert parsed == [{b"Name": b"Jane", b"Preference": b"Ice Cream"}]


def test_aligned():
    data: list[bytes] = [b"Name", b" John"]

    parsed: list[dict[bytes, bytes]] = _parse(data[0], data[1:])
    assert parsed == [{b"Name": b"John"}]


def test_empty_body():
    data: list[bytes] = [b"Name", b""]

    parsed: list[dict[bytes, bytes]] = _parse(data[0], data[1:])
    assert parsed == [{}]


def test_space_body():
    for space_length in range(1, 8):
        data: list[bytes] = [b"Name", b" " * space_length]

        parsed: list[dict[bytes, bytes]] = _parse(data[0], data[1:])
        assert parsed == [{}]
