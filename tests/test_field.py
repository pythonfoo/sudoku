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
    f = Field("asdf123reaf213")
    assert len(f.cells) == 81


def test_single() -> None:
    f = Field("")
    group = [
        DCell(hopeful={1, 2, 3, 4, 5}, position=1),
        DCell(hopeful={2, 3, 4, 5}, position=2),
        DCell(hopeful={2}, position=3),
    ]
    actions = list(
        sorted(
            f.singles(
                type="test",
                idx=1,
                group=set(group),
            )
        )
    )
    assert len(actions) == 1
    assert actions[0].cell == group[0]
    assert actions[0].value == 1


def test_solved() -> None:
    f = Field("")
    group = [
        DCell(hopeful={1, 2, 3, 4, 5}, position=1),
        DCell(hopeful={2, 3, 4, 5}, position=2),
        DCell(hopeful={2}, position=3),
    ]
    actions = list(
        sorted(
            f.solved(
                type="test",
                idx=1,
                group=set(group),
            )
        )
    )
    assert len(actions) == 1
    assert actions[0].cell == group[2]
    assert actions[0].value == 2


def test_show_possibles() -> None:
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
                type="test",
                idx=1,
                group=set(group),
            )
        )
    )
    print(actions)
    assert len(actions) == 2
    assert actions[0].cell == group[0]
    assert actions[0].value == 3


def test_naked_pairs() -> None:
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
                type="test",
                idx=1,
                group=set(group),
            )
        )
    )
    print(actions)
    assert len(actions) == 6
    assert actions[0].cell == group[0]
    assert actions[0].value == 2
    assert actions[3].value == 4


def test_naked_triples() -> None:
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
                type="test",
                idx=1,
                group=set(group),
            )
        )
    )
    print(actions)
    assert len(actions) == 3
    assert actions[0].cell == group[0]
    assert actions[0].value == 2
    assert actions[1].value == 4
    assert actions[2].value == 5


def test_pointing_pairs() -> None:
    f = Field("0" * 81)
    f.load(Path("tests/savegames/pointing_pairs.savegame"))

    actions = list(
        sorted(
            f.pointing_pairs(
                idx=0,
            )
        )
    )
    print(actions)
    assert len(actions) == 3
    assert actions[0].cell == f.get_cell(3, 0)
    assert actions[0].value == 2
    assert actions[1].cell == f.get_cell(4, 0)
    assert actions[1].value == 2
    assert actions[2].cell == f.get_cell(5, 0)
    assert actions[2].value == 2


def test_hidden_pairs() -> None:
    """
    identify hidden pair 6,7 in first row (idx 7 and 8)
    """
    f = Field("0" * 81)
    f.load(Path("tests/savegames/hidden_pairs.savegame"))
    actions = list(sorted(f.hidden_pairs(idx=0, group_types=["row"])))
    print(actions)
    assert len(actions) == 9

    positions = set(a.cell.position.as_int() for a in actions)
    assert len(positions) == 2
    values = set(a.value for a in actions)

    assert (
        values.intersection({6, 7}) == set()
    ), "don't remove members of the hidden pair"


def test_hidden_tripples() -> None:
    f = Field("0" * 81)
    f.load(Path("tests/savegames/hidden_tripples.savegame"))
    actions = list(sorted(f.hidden_tripples()))
    for action in actions:
        print(f"{action.value} {action.reason}")
    assert len(actions) == 9

    positions = set(a.cell.position.as_int() for a in actions)
    assert len(positions) == 3
    values = set(a.value for a in actions)

    assert (
        values.intersection({2, 5, 6}) == set()
    ), "don't remove members of the hidden tripple"


def test_box_line_reduction() -> None:
    f = Field("0" * 81)
    f.load(Path("tests/savegames/box_line_reduction.savegame"))
    actions = list(sorted(f.box_line_reduction()))
    for action in actions:
        print(
            f"{action.action} {action.value} from {action.cell.position} {action.reason}"
        )
    assert len(actions) == 3

    positions = set(a.cell.position.as_int() for a in actions)
    assert len(positions) == 3
    values = set(a.value for a in actions)

    assert len(values) == 1
    assert actions[0].value == 4


def test_xwing() -> None:
    f = Field("0" * 81)
    f.load(Path("tests/savegames/xwing.savegame"))
    actions = list(sorted(f.xwing()))
    for action in actions:
        print(
            f"{action.action} {action.value} from {action.cell.position} {action.reason}"
        )
    assert len(actions) == 6

    positions = set(a.cell.position.as_int() for a in actions)
    assert len(positions) == 6
    values = set(a.value for a in actions)

    assert len(values) == 1
    assert actions[0].value == 7


def test_single_chains() -> None:
    f = Field("0" * 81)
    f.load(Path("tests/savegames/single_chains.savegame"))
    actions = list(sorted(f.single_chains()))
    for action in actions:
        print(
            f"{action.action} {action.value} from {action.cell.position} {action.reason}"
        )
    assert len(actions) == 3

    positions = set(a.cell.position.as_int() for a in actions)
    assert len(positions) == 3
    values = set(a.value for a in actions)

    assert len(values) == 1
    assert actions[0].value == 7


if __name__ == "__main__":
    pytest.main(["-k", "field"])
