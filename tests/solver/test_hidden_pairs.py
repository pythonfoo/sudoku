from typing import NamedTuple

import pytest

from sudoku.cell import Cell
from sudoku.field import Field
from sudoku.solver.hidden_pairs import hidden_pairs
from sudoku.types import CellPosition


class MockCell(NamedTuple):
    """Mock cell for testing purposes"""

    position: CellPosition
    hopeful: set[int]
    value: int = 0

    def __hash__(self) -> int:
        return self.position.as_int()


def _pos(x: int, y: int) -> CellPosition:
    return CellPosition(x, y)


def test_hidden_pairs_basic_elimination():
    """
    Basic hidden pair scenario:
    Two numbers (3 and 7) appear exactly in the same two cells within the group.
    The solver should remove other candidates from those two cells.
    """
    field = Field("0" * 81)

    # The two cells that will form the hidden pair for {3, 7}
    # Make sure 8 and 9 appear in other cells too so they don't form singleton hidden pairs
    # Also ensure 1 and 2 don't form a hidden pair by spreading them across cells
    cell1 = MockCell(position=_pos(0, 0), hopeful={3, 7, 8})
    cell2 = MockCell(position=_pos(1, 0), hopeful={3, 7, 9})
    cell3 = MockCell(position=_pos(2, 0), hopeful={1, 8})  # Contains 8 and 1
    cell4 = MockCell(position=_pos(3, 0), hopeful={2, 9})  # Contains 9 and 2

    group = {cell1, cell2, cell3, cell4}

    actions = list(hidden_pairs(field, type="row", idx=0, group=group))

    # Expect removal of 8 from cell1 and 9 from cell2 (two actions)
    assert len(actions) == 2

    actions_by_cell = {}
    for a in actions:
        actions_by_cell.setdefault(a.cell, set()).add(a.value)
        assert a.action == "remove_possible"
        assert "hidden pair" in a.reason or "hidden pair" in a.reason.lower()

    assert actions_by_cell[cell1] == {8}
    assert actions_by_cell[cell2] == {9}
    # Ensure no other cell was targeted
    assert cell3 not in actions_by_cell
    assert cell4 not in actions_by_cell


def test_hidden_pairs_no_action_when_not_hidden():
    """
    If no two numbers share the exact same occurrence set, there should be no actions.
    """
    field = Field("0" * 81)

    cell1 = MockCell(position=_pos(0, 1), hopeful={1, 2})
    cell2 = MockCell(position=_pos(1, 1), hopeful={2, 3})
    cell3 = MockCell(position=_pos(2, 1), hopeful={3, 4})
    cell4 = MockCell(position=_pos(3, 1), hopeful={4, 5})

    group = {cell1, cell2, cell3, cell4}

    actions = list(hidden_pairs(field, type="row", idx=1, group=group))
    assert len(actions) == 0


def test_hidden_pairs_ignores_numbers_in_more_than_two_cells():
    """
    Numbers that appear in more than two cells are ignored by the algorithm.
    Even if two numbers appear in the same >2 cells, they should not be treated
    as a hidden pair.
    """
    field = Field("0" * 81)

    # Create three cells that all contain 6 and 7 -> counts > 2, should be ignored
    c1 = MockCell(position=_pos(0, 2), hopeful={6, 7, 1})
    c2 = MockCell(position=_pos(1, 2), hopeful={6, 7, 2})
    c3 = MockCell(position=_pos(2, 2), hopeful={6, 7, 3})
    c4 = MockCell(position=_pos(3, 2), hopeful={4})

    group = {c1, c2, c3, c4}

    actions = list(hidden_pairs(field, type="row", idx=2, group=group))
    assert len(actions) == 0


def test_hidden_pairs_with_real_cells():
    """
    Integration-style test that uses real Cell objects from the Field to ensure
    the solver works with actual Cell instances.
    """
    field = Field("0" * 81)

    # Use real cells from the field (row 0)
    real_c1 = field.get_cell(0, 0)
    real_c2 = field.get_cell(1, 0)
    real_c3 = field.get_cell(2, 0)

    # Set up hopeful sets so that 4 and 7 appear only in real_c1 and real_c2
    # and both cells contain additional candidates that should be removed.
    real_c1.hopeful = {4, 7, 8}
    real_c2.hopeful = {4, 7, 9}
    real_c3.hopeful = {1, 6}

    group = {real_c1, real_c2, real_c3}

    actions = list(hidden_pairs(field, type="row", idx=0, group=group))

    # Expect removal of 8 from real_c1 and 9 from real_c2
    assert len(actions) == 2
    removals = {a.cell: set() for a in actions}
    for a in actions:
        removals.setdefault(a.cell, set()).add(a.value)
        assert a.action == "remove_possible"

    assert removals.get(real_c1) == {8}
    assert removals.get(real_c2) == {9}
