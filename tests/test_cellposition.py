from typing import Tuple

import pytest

from sudoku.types import CellPosition


def test_from_int_and_as_int_roundtrip() -> None:
    # Ensure every int in 0..80 round-trips through from_int and as_int
    for i in range(81):
        pos = CellPosition.from_int(i)
        assert isinstance(pos, CellPosition)
        assert pos.as_int() == i


@pytest.mark.parametrize(
    "x,y,expected_block",
    [
        (0, 0, 0),  # top-left
        (8, 0, 2),  # top-right
        (0, 8, 6),  # bottom-left
        (8, 8, 8),  # bottom-right
        (4, 4, 4),  # center
        (3, 0, 1),  # first row, second block
        (2, 3, 3),  # left block of middle band
    ],
)
def test_block_property(x: int, y: int, expected_block: int) -> None:
    pos = CellPosition(x, y)
    assert pos.block == expected_block
    # row should reflect y, column should reflect x
    assert pos.row == y
    assert pos.column == x


def test_from_xy_and_attributes() -> None:
    pos = CellPosition.from_xy(2, 5)
    assert isinstance(pos, CellPosition)
    assert pos.x == 2
    assert pos.y == 5
    assert pos.column == 2
    assert pos.row == 5
    # as_int consistency
    assert pos.as_int() == 5 * 9 + 2


@pytest.mark.parametrize(
    "s,expected",
    [
        ("A1", (0, 0)),
        ("I9", (8, 8)),
        ("B3", (2, 1)),
        ("e5", (4, 4)),  # lowercase input should work
    ],
)
def test_from_sudokuwiki_and_str(s: str, expected: Tuple[int, int]) -> None:
    pos = CellPosition.from_sudokuwiki(s)
    print(s, str(pos))
    exp_x, exp_y = expected
    assert pos.x == exp_x
    assert pos.y == exp_y
    # __str__ should produce the canonical sudokuwiki representation (uppercase letter + digit)
    assert str(pos) == s.upper()
