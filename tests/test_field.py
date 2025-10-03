from pathlib import Path
from typing import List, NamedTuple

import pytest

from sudoku.field import Field


class DCell(NamedTuple):
    position: int
    hopeful: set[int]
    value: int = 0

    def __hash__(self) -> int:
        return self.position


def test_field() -> None:
    f = Field(
        "100400006046091080005020000000500109090000050402009000000010900080930560500008004"
    )
    assert len(f.cells) == 81


if __name__ == "__main__":
    pytest.main(["-k", "field"])
