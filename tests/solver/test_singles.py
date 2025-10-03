from collections import defaultdict
from typing import NamedTuple

import pytest

from sudoku.action import Action
from sudoku.cell import Cell
from sudoku.field import Field
from sudoku.solver.singles import singles
from sudoku.types import CellPosition


class MockCell(NamedTuple):
    """Mock cell for testing purposes"""

    position: CellPosition
    hopeful: set[int]
    value: int = 0

    def __hash__(self) -> int:
        return self.position.as_int()


def test_singles_single_possibility_for_number():
    """Test that a number with only one possible cell generates a set_number action"""
    field = Field("")

    # Create cells where number 5 can only go in one cell
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={1, 2, 3})  # No 5
    cell2 = MockCell(
        position=CellPosition(1, 0), hopeful={5, 6, 7}
    )  # Has 5 - only cell that can have 5
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={8, 9})  # No 5
    group = {cell1, cell2, cell3}

    actions = list(singles(field, type="row", idx=0, group=group))

    # Should generate one action for number 5
    actions_for_5 = [a for a in actions if a.value == 5]
    assert len(actions_for_5) == 1

    action = actions_for_5[0]
    assert action.action == "set_number"
    assert action.value == 5
    assert action.cell == cell2
    assert "single 5 found in row at" in action.reason


def test_singles_multiple_single_possibilities():
    """Test multiple numbers that each have only one possible cell"""
    field = Field("")

    # Create cells where numbers 1, 5, and 9 each have only one possible location
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={1, 2, 3})  # Only cell for 1
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={4, 5, 6})  # Only cell for 5
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={7, 8, 9})  # Only cell for 9
    cell4 = MockCell(
        position=CellPosition(3, 0), hopeful={2, 3, 4, 6, 7, 8}
    )  # No singles
    group = {cell1, cell2, cell3, cell4}

    actions = list(singles(field, type="row", idx=0, group=group))

    # Should generate 3 actions (for numbers 1, 5, 9)
    single_values = {a.value for a in actions}
    assert single_values == {1, 5, 9}
    assert len(actions) == 3

    # Sort actions by value for consistent testing
    actions.sort(key=lambda a: a.value)

    # Verify each action
    assert actions[0].value == 1 and actions[0].cell == cell1
    assert actions[1].value == 5 and actions[1].cell == cell2
    assert actions[2].value == 9 and actions[2].cell == cell3

    # All should be set_number actions with correct reasons
    for action in actions:
        assert action.action == "set_number"
        assert f"single {action.value} found in row at" in action.reason


def test_singles_no_single_possibilities():
    """Test that numbers with multiple possible cells don't generate actions"""
    field = Field("")

    # Create cells where all numbers have multiple possible locations
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={1, 2, 3, 4, 5})
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={1, 2, 6, 7, 8})
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={3, 4, 6, 7, 9})
    group = {cell1, cell2, cell3}

    actions = list(singles(field, type="row", idx=0, group=group))

    # Should generate no actions since no number has a single location
    # Numbers 1,3,4,6,7 appear in multiple cells, 5,8,9 each appear in only one cell
    # So we should get actions for 5,8,9
    single_values = {a.value for a in actions}
    assert single_values == {5, 8, 9}
    assert len(actions) == 3


def test_singles_mixed_group():
    """Test a group with mix of single and multiple possibilities"""
    field = Field("")

    # Mix: some numbers have single locations, others have multiple
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={1, 2, 3})  # 1 is single here
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={2, 3, 4})  # 4 is single here
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={2, 3, 5})  # 5 is single here
    cell4 = MockCell(
        position=CellPosition(3, 0), hopeful={6, 7, 8}
    )  # 6,7,8 are singles here
    group = {cell1, cell2, cell3, cell4}

    actions = list(singles(field, type="column", idx=0, group=group))

    # Numbers 2,3 appear in multiple cells (no action)
    # Numbers 1,4,5,6,7,8 each appear in only one cell (should get actions)
    single_values = {a.value for a in actions}
    assert single_values == {1, 4, 5, 6, 7, 8}
    assert len(actions) == 6

    # Verify the actions target correct cells
    actions_dict = {a.value: a.cell for a in actions}
    assert actions_dict[1] == cell1
    assert actions_dict[4] == cell2
    assert actions_dict[5] == cell3
    assert actions_dict[6] == cell4
    assert actions_dict[7] == cell4
    assert actions_dict[8] == cell4


def test_singles_empty_group():
    """Test with an empty group"""
    field = Field("")
    group = set()

    actions = list(singles(field, type="row", idx=0, group=group))

    # Should generate no actions
    assert len(actions) == 0


def test_singles_cells_with_empty_hopeful():
    """Test cells with empty hopeful sets (already solved cells)"""
    field = Field("")

    # Cells with empty hopeful sets (typically means they're already solved)
    cell1 = MockCell(position=CellPosition(0, 0), hopeful=set(), value=5)
    cell2 = MockCell(position=CellPosition(1, 0), hopeful=set(), value=3)
    cell3 = MockCell(
        position=CellPosition(2, 0), hopeful={1, 2, 4}
    )  # This cell has possibilities
    group = {cell1, cell2, cell3}

    actions = list(singles(field, type="row", idx=0, group=group))

    # Should generate actions for numbers that appear in only cell3
    single_values = {a.value for a in actions}
    assert single_values == {1, 2, 4}
    assert len(actions) == 3

    # All actions should target cell3
    for action in actions:
        assert action.cell == cell3


def test_singles_with_real_cells():
    """Test with actual Cell objects instead of mock objects"""
    field = Field("")

    # Create real Cell objects
    cell1 = Cell(0, CellPosition(0, 0))
    cell2 = Cell(0, CellPosition(1, 0))
    cell3 = Cell(0, CellPosition(2, 0))

    # Manually set hopeful values to simulate the solving state
    cell1.hopeful = {1, 2, 3}  # 1 is single
    cell2.hopeful = {2, 3, 4}  # 4 is single
    cell3.hopeful = {2, 3, 5}  # 5 is single
    # Numbers 2,3 appear in multiple cells

    group = {cell1, cell2, cell3}

    actions = list(singles(field, type="block", idx=0, group=group))

    # Should generate actions for numbers 1, 4, 5
    single_values = {a.value for a in actions}
    assert single_values == {1, 4, 5}
    assert len(actions) == 3

    # Verify action details
    actions_dict = {a.value: a.cell for a in actions}
    assert actions_dict[1] == cell1
    assert actions_dict[4] == cell2
    assert actions_dict[5] == cell3

    for action in actions:
        assert action.action == "set_number"
        assert f"single {action.value} found in block at" in action.reason


def test_singles_reason_format():
    """Test that the reason string is formatted correctly"""
    field = Field("")
    cell_pos = CellPosition(3, 4)
    mock_cell = MockCell(position=cell_pos, hopeful={7})
    group = {mock_cell}

    actions = list(singles(field, type="column", idx=4, group=group))

    assert len(actions) == 1
    action = actions[0]

    # Verify the reason format
    expected_reason = f"single 7 found in column at {cell_pos}"
    assert action.reason == expected_reason


def test_singles_comprehensive_scenario():
    """Test a comprehensive scenario with various cell configurations"""
    field = Field("")

    # Create a realistic scenario
    cells = [
        MockCell(position=CellPosition(0, 0), hopeful={1, 4, 7}),  # 1,4,7 compete
        MockCell(
            position=CellPosition(1, 0), hopeful={1, 4, 8}
        ),  # 1,4 compete, 8 is single
        MockCell(
            position=CellPosition(2, 0), hopeful={2, 5, 7}
        ),  # 2,5 compete, 7 competes
        MockCell(
            position=CellPosition(3, 0), hopeful={2, 5, 9}
        ),  # 2,5 compete, 9 is single
        MockCell(position=CellPosition(4, 0), hopeful={3, 6}),  # 3,6 are singles
        MockCell(position=CellPosition(5, 0), hopeful=set()),  # Already solved
        MockCell(position=CellPosition(6, 0), hopeful={1, 4}),  # 1,4 compete
        MockCell(
            position=CellPosition(7, 0), hopeful={7}
        ),  # 7 competes but also single here
        MockCell(position=CellPosition(8, 0), hopeful={2, 5}),  # 2,5 compete
    ]

    group = set(cells)
    actions = list(singles(field, type="row", idx=0, group=group))

    # Expected singles:
    # 8 only in cell[1]
    # 9 only in cell[3]
    # 3 only in cell[4]
    # 6 only in cell[4]
    # Note: 7 appears in cells[0], cells[2], and cells[7], so it should generate action for cells[7] only
    # since cells[7] is the only one with 7 as sole option? No, that's wrong.
    # 7 appears in cells[0], cells[2], cells[7] - so it's NOT a single

    # Let me recalculate:
    # 1: appears in cells[0], cells[1], cells[6] - not single
    # 2: appears in cells[2], cells[3], cells[8] - not single
    # 3: appears only in cells[4] - SINGLE
    # 4: appears in cells[0], cells[1], cells[6] - not single
    # 5: appears in cells[2], cells[3], cells[8] - not single
    # 6: appears only in cells[4] - SINGLE
    # 7: appears in cells[0], cells[2], cells[7] - not single
    # 8: appears only in cells[1] - SINGLE
    # 9: appears only in cells[3] - SINGLE

    single_values = {a.value for a in actions}
    assert single_values == {3, 6, 8, 9}
    assert len(actions) == 4

    # Verify correct cell assignments
    actions_dict = {a.value: a.cell for a in actions}
    assert actions_dict[3] == cells[4]  # 3 only in cell 4
    assert actions_dict[6] == cells[4]  # 6 only in cell 4
    assert actions_dict[8] == cells[1]  # 8 only in cell 1
    assert actions_dict[9] == cells[3]  # 9 only in cell 3


def test_singles_duplicate_numbers_different_cells():
    """Test that the same number appearing in multiple cells is handled correctly"""
    field = Field("")

    # Create scenario where number 5 appears in multiple cells
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={5, 6, 7})
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={5, 8, 9})
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={1, 2, 3})
    group = {cell1, cell2, cell3}

    actions = list(singles(field, type="row", idx=0, group=group))

    # Number 5 appears in 2 cells, so should not generate action
    # Numbers 1,2,3,6,7,8,9 each appear in only one cell
    single_values = {a.value for a in actions}
    assert 5 not in single_values
    assert single_values == {1, 2, 3, 6, 7, 8, 9}
    assert len(actions) == 7


if __name__ == "__main__":
    pytest.main([__file__])
