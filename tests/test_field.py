from typing import List, NamedTuple
from dataclasses import dataclass
import pytest
from sudoku.field import Field


class DCell(NamedTuple):
    position: int
    hopeful: List[int]
    value: int = 0

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


def test_solved():
    f = Field("")
    group = [
        DCell(hopeful={1, 2, 3, 4, 5}, position=1),
        DCell(hopeful={2, 3, 4, 5}, position=2),
        DCell(hopeful={2}, position=3),
    ]
    actions = list(
        sorted(
            f.solved(
                group=set(group),
                idx=1,
            )
        )
    )
    assert len(actions) == 1
    assert actions[0].cell == group[2]
    assert actions[0].value == 2


def test_show_possibles():
    f = Field("")
    group = [
        DCell(hopeful={1, 2, 3, 4, 5}, position=1),
        DCell(hopeful={2, 3, 4, 5}, position=2),
        DCell(hopeful={2}, position=3),
        DCell(hopeful={}, value=3, position=4),
    ]
    actions = list(
        sorted(
            f.show_possibles(
                group=set(group),
                idx=1,
            )
        )
    )
    print(actions)
    assert len(actions) == 2
    assert actions[0].cell == group[0]
    assert actions[0].value == 3


def test_naked_pairs():
    f = Field("")
    group = [
        DCell(hopeful={1, 2, 3, 4, 5}, position=1),
        DCell(hopeful={2, 3, 4, 5}, position=2),
        DCell(hopeful={2, 4}, position=3),
        DCell(hopeful={}, value=3, position=4),
        DCell(hopeful={2, 4}, position=5),
        DCell(hopeful={2, 5}, position=6),
        DCell(hopeful={4, 5}, position=7),
    ]
    actions = list(
        sorted(
            f.naked_pairs(
                group=set(group),
                idx=1,
            )
        )
    )
    print(actions)
    assert len(actions) == 6
    assert actions[0].cell == group[0]
    assert actions[0].value == 2
    assert actions[3].value == 4


def test_naked_triples():
    f = Field("")
    group = [
        DCell(hopeful={1, 2, 3, 4, 5}, position=1),
        DCell(hopeful={3}, position=2),
        DCell(hopeful={2, 4}, position=3),
        DCell(hopeful={4, 5}, position=4),
        DCell(hopeful={2, 5}, position=5),
    ]
    actions = list(
        sorted(
            f.naked_triples(
                group=set(group),
                idx=1,
            )
        )
    )
    print(actions)
    assert len(actions) == 3
    assert actions[0].cell == group[0]
    assert actions[0].value == 2
    assert actions[1].value == 4
    assert actions[2].value == 5


# "naked_triples",