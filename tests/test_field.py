from typing import List, NamedTuple
from dataclasses import dataclass
import pytest
from sudoku.field import Field


@dataclass()
class DCell:
    hopeful: List[int]
    position: int

    def __hash__(self):
        return self.position


def test_field():
    f = Field("asdf123reaf213")


def test_single():
    f = Field("")
    group = [
        DCell(hopeful={1, 2, 3, 4, 5}, position=1),
        DCell(hopeful={2, 3, 4, 5}, position=2),
        DCell(hopeful={2}, position=3),
    ]
    actions = list(
        sorted(
            f.singles(
                group=set(group),
                idx=1,
            )
        )
    )
    assert len(actions) == 1
    assert actions[0].cell == group[0]
    assert actions[0].value == 1
