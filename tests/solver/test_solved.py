from typing import NamedTuple

import pytest

from sudoku.action import Action
from sudoku.cell import Cell
from sudoku.field import Field
from sudoku.solver.solved import solved
from sudoku.types import CellPosition


class MockCell(NamedTuple):
    """Mock cell for testing purposes"""

    position: CellPosition
    hopeful: set[int]
    value: int = 0

    def __hash__(self) -> int:
        return self.position.as_int()


def test_solved_single_cell_with_one_hopeful():
    """Test that a cell with exactly one hopeful value generates a set_number action"""
    field = Field("")  # Create a field (content doesn't matter for this test)

    # Create a cell with only one possible value
    cell_pos = CellPosition(0, 0)
    mock_cell = MockCell(position=cell_pos, hopeful={5})
    group = {mock_cell}

    # Call the solved function directly
    actions = list(solved(field, type="row", idx=0, group=group))

    # Verify the action
    assert len(actions) == 1
    action = actions[0]
    assert action.action == "set_number"
    assert action.value == 5
    assert action.cell == mock_cell
    assert "solved cell 5 found at" in action.reason
    assert str(cell_pos) in action.reason


def test_solved_multiple_cells_with_one_hopeful():
    """Test multiple cells each with one hopeful value"""
    field = Field("")

    # Create multiple cells with single hopeful values
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={3})
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={7})
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={1})
    group = {cell1, cell2, cell3}

    actions = list(solved(field, type="row", idx=0, group=group))

    # Should generate 3 actions
    assert len(actions) == 3

    # Sort actions by cell position for consistent testing
    actions.sort(key=lambda a: a.cell.position.as_int())

    # Verify each action
    assert actions[0].value == 3
    assert actions[0].cell == cell1
    assert actions[1].value == 7
    assert actions[1].cell == cell2
    assert actions[2].value == 1
    assert actions[2].cell == cell3

    # All should be set_number actions
    for action in actions:
        assert action.action == "set_number"
        assert "solved cell" in action.reason


def test_solved_no_single_hopeful_cells():
    """Test that cells with multiple hopeful values don't generate actions"""
    field = Field("")

    # Create cells with multiple hopeful values
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={1, 2, 3})
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={4, 5})
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={6, 7, 8, 9})
    group = {cell1, cell2, cell3}

    actions = list(solved(field, type="row", idx=0, group=group))

    # Should generate no actions
    assert len(actions) == 0


def test_solved_mixed_group():
    """Test a group with mix of single and multiple hopeful cells"""
    field = Field("")

    # Mix of cells: some with single hopeful, some with multiple
    cell1 = MockCell(
        position=CellPosition(0, 0), hopeful={9}
    )  # Single - should generate action
    cell2 = MockCell(
        position=CellPosition(1, 0), hopeful={1, 2}
    )  # Multiple - no action
    cell3 = MockCell(
        position=CellPosition(2, 0), hopeful={4}
    )  # Single - should generate action
    cell4 = MockCell(
        position=CellPosition(3, 0), hopeful={5, 6, 7}
    )  # Multiple - no action
    group = {cell1, cell2, cell3, cell4}

    actions = list(solved(field, type="row", idx=0, group=group))

    # Should generate 2 actions (for cells with single hopeful)
    assert len(actions) == 2

    # Sort actions by cell position
    actions.sort(key=lambda a: a.cell.position.as_int())

    # Verify only the single-hopeful cells generated actions
    assert actions[0].cell == cell1
    assert actions[0].value == 9
    assert actions[1].cell == cell3
    assert actions[1].value == 4


def test_solved_empty_group():
    """Test with an empty group"""
    field = Field("")
    group = set()

    actions = list(solved(field, type="row", idx=0, group=group))

    # Should generate no actions
    assert len(actions) == 0


def test_solved_cells_with_empty_hopeful():
    """Test cells with empty hopeful sets (already solved cells)"""
    field = Field("")

    # Cells with empty hopeful sets (typically means they're already solved)
    cell1 = MockCell(position=CellPosition(0, 0), hopeful=set(), value=5)
    cell2 = MockCell(position=CellPosition(1, 0), hopeful=set(), value=3)
    group = {cell1, cell2}

    actions = list(solved(field, type="row", idx=0, group=group))

    # Should generate no actions
    assert len(actions) == 0


def test_solved_with_real_cells():
    """Test with actual Cell objects instead of mock objects"""
    field = Field("")

    # Create real Cell objects
    cell1 = Cell(0, CellPosition(0, 0))
    cell2 = Cell(0, CellPosition(1, 0))
    cell3 = Cell(0, CellPosition(2, 0))

    # Manually set hopeful values to simulate the solving state
    cell1.hopeful = {8}  # Single hopeful value
    cell2.hopeful = {2, 4, 6}  # Multiple hopeful values
    cell3.hopeful = {1}  # Single hopeful value

    group = {cell1, cell2, cell3}

    actions = list(solved(field, type="column", idx=0, group=group))

    # Should generate 2 actions (for cells with single hopeful)
    assert len(actions) == 2

    # Sort actions by cell position
    actions.sort(key=lambda a: a.cell.position.as_int())

    # Verify the actions
    assert actions[0].cell == cell1
    assert actions[0].value == 8
    assert actions[1].cell == cell3
    assert actions[1].value == 1

    # Verify action details
    for action in actions:
        assert action.action == "set_number"
        assert "solved cell" in action.reason
        assert "found at" in action.reason


def test_solved_reason_format():
    """Test that the reason string is formatted correctly"""
    field = Field("")
    cell_pos = CellPosition(3, 4)  # Specific position for testing
    mock_cell = MockCell(position=cell_pos, hopeful={6})
    group = {mock_cell}

    actions = list(solved(field, type="block", idx=4, group=group))

    assert len(actions) == 1
    action = actions[0]

    # Verify the reason format
    expected_reason = f"solved cell 6 found at {cell_pos}"
    assert action.reason == expected_reason
