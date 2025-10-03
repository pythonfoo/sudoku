from typing import NamedTuple

import pytest

from sudoku.action import Action
from sudoku.cell import Cell
from sudoku.field import Field
from sudoku.solver.show_possibles import show_possibles
from sudoku.types import CellPosition


class MockCell(NamedTuple):
    """Mock cell for testing purposes"""

    position: CellPosition
    hopeful: set[int]
    value: int = 0

    def __hash__(self) -> int:
        return self.position.as_int()


def test_show_possibles_basic_elimination():
    """Test basic elimination: cell with value 5 eliminates 5 from other cells' hopeful sets"""
    field = Field("")

    # Create cells: one with value 5, others with 5 in their hopeful sets
    cell1 = MockCell(position=CellPosition(0, 0), hopeful=set(), value=5)  # Has value 5
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={1, 2, 5, 6})  # Should lose 5
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={3, 5, 7, 8})  # Should lose 5
    cell4 = MockCell(
        position=CellPosition(3, 0), hopeful={1, 2, 3, 4}
    )  # No 5, no change

    group = {cell1, cell2, cell3, cell4}

    actions = list(show_possibles(field, type="row", idx=0, group=group))

    # Should generate 2 actions: remove 5 from cell2 and cell3
    assert len(actions) == 2

    # Sort actions by cell position for consistent testing
    actions.sort(key=lambda a: a.cell.position.as_int())

    # Verify first action (cell2)
    assert actions[0].action == "remove_possible"
    assert actions[0].value == 5
    assert actions[0].cell == cell2
    assert actions[0].reason  # Just verify reason is not empty

    # Verify second action (cell3)
    assert actions[1].action == "remove_possible"
    assert actions[1].value == 5
    assert actions[1].cell == cell3
    assert actions[1].reason  # Just verify reason is not empty


def test_show_possibles_multiple_values():
    """Test elimination with multiple solved cells"""
    field = Field("")

    # Create cells with different values
    cell1 = MockCell(position=CellPosition(0, 0), hopeful=set(), value=3)  # Has value 3
    cell2 = MockCell(position=CellPosition(1, 0), hopeful=set(), value=7)  # Has value 7
    cell3 = MockCell(
        position=CellPosition(2, 0), hopeful={1, 3, 5, 7, 9}
    )  # Should lose 3 and 7
    cell4 = MockCell(
        position=CellPosition(3, 0), hopeful={2, 3, 4, 6, 8}
    )  # Should lose 3
    cell5 = MockCell(position=CellPosition(4, 0), hopeful={1, 2, 4, 5, 6})  # No 3 or 7

    group = {cell1, cell2, cell3, cell4, cell5}

    actions = list(show_possibles(field, type="column", idx=0, group=group))

    # Should generate 3 actions: remove 3 from cell3, remove 7 from cell3, remove 3 from cell4
    assert len(actions) == 3

    # Group actions by value for easier verification
    actions_by_value = {}
    for action in actions:
        if action.value not in actions_by_value:
            actions_by_value[action.value] = []
        actions_by_value[action.value].append(action)

    # Verify actions for value 3
    assert len(actions_by_value[3]) == 2
    cells_losing_3 = {a.cell for a in actions_by_value[3]}
    assert cells_losing_3 == {cell3, cell4}

    # Verify actions for value 7
    assert len(actions_by_value[7]) == 1
    assert actions_by_value[7][0].cell == cell3

    # Verify all actions have correct properties
    for action in actions:
        assert action.action == "remove_possible"
        assert action.reason  # Just verify reason is not empty


def test_show_possibles_no_eliminations():
    """Test case where no eliminations are possible"""
    field = Field("")

    # Create cells where no eliminations are needed
    cell1 = MockCell(position=CellPosition(0, 0), hopeful=set(), value=5)  # Has value 5
    cell2 = MockCell(
        position=CellPosition(1, 0), hopeful={1, 2, 3, 4}
    )  # No 5 in hopeful
    cell3 = MockCell(
        position=CellPosition(2, 0), hopeful={6, 7, 8, 9}
    )  # No 5 in hopeful
    cell4 = MockCell(position=CellPosition(3, 0), hopeful=set(), value=1)  # Has value 1

    group = {cell1, cell2, cell3, cell4}

    actions = list(show_possibles(field, type="block", idx=0, group=group))

    # Should generate 1 action: remove 1 from cell2 (cell4 has value 1)
    assert len(actions) == 1
    action = actions[0]
    assert action.action == "remove_possible"
    assert action.value == 1
    assert action.cell == cell2
    assert action.reason  # Just verify reason is not empty


def test_show_possibles_all_cells_solved():
    """Test case where all cells are already solved"""
    field = Field("")

    # All cells have values (no hopeful sets)
    cell1 = MockCell(position=CellPosition(0, 0), hopeful=set(), value=1)
    cell2 = MockCell(position=CellPosition(1, 0), hopeful=set(), value=2)
    cell3 = MockCell(position=CellPosition(2, 0), hopeful=set(), value=3)
    cell4 = MockCell(position=CellPosition(3, 0), hopeful=set(), value=4)

    group = {cell1, cell2, cell3, cell4}

    actions = list(show_possibles(field, type="row", idx=0, group=group))

    # Should generate no actions since all cells are solved
    assert len(actions) == 0


def test_show_possibles_empty_group():
    """Test with an empty group"""
    field = Field("")
    group = set()

    actions = list(show_possibles(field, type="row", idx=0, group=group))

    # Should generate no actions
    assert len(actions) == 0


def test_show_possibles_single_cell_group():
    """Test with a group containing only one cell"""
    field = Field("")

    cell1 = MockCell(position=CellPosition(0, 0), hopeful={1, 2, 3}, value=0)
    group = {cell1}

    actions = list(show_possibles(field, type="row", idx=0, group=group))

    # Should generate no actions since there's only one cell
    assert len(actions) == 0


def test_show_possibles_no_solved_cells():
    """Test case where no cells are solved (all have value 0)"""
    field = Field("")

    # All cells have value 0 (unsolved)
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={1, 2, 3}, value=0)
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={4, 5, 6}, value=0)
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={7, 8, 9}, value=0)

    group = {cell1, cell2, cell3}

    actions = list(show_possibles(field, type="column", idx=0, group=group))

    # Should generate no actions since no cells are solved
    assert len(actions) == 0


def test_show_possibles_complex_scenario():
    """Test a complex scenario with multiple solved cells and various hopeful sets"""
    field = Field("")

    # Complex scenario with multiple eliminations
    cell1 = MockCell(position=CellPosition(0, 0), hopeful=set(), value=1)  # Solved: 1
    cell2 = MockCell(position=CellPosition(1, 0), hopeful=set(), value=5)  # Solved: 5
    cell3 = MockCell(position=CellPosition(2, 0), hopeful=set(), value=9)  # Solved: 9
    cell4 = MockCell(position=CellPosition(0, 1), hopeful={1, 2, 3, 4})  # Should lose 1
    cell5 = MockCell(
        position=CellPosition(1, 1), hopeful={1, 5, 6, 7}
    )  # Should lose 1, 5
    cell6 = MockCell(position=CellPosition(2, 1), hopeful={2, 8, 9})  # Should lose 9
    cell7 = MockCell(
        position=CellPosition(0, 2), hopeful={3, 4, 6, 7}
    )  # No eliminations
    cell8 = MockCell(
        position=CellPosition(1, 2), hopeful={1, 2, 5, 8}
    )  # Should lose 1, 5
    cell9 = MockCell(position=CellPosition(2, 2), hopeful={2, 3, 4, 9})  # Should lose 9

    group = {cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8, cell9}

    actions = list(show_possibles(field, type="block", idx=0, group=group))

    # Expected eliminations:
    # Value 1: from cell4, cell5, cell8 (3 actions)
    # Value 5: from cell5, cell8 (2 actions)
    # Value 9: from cell6, cell9 (2 actions)
    # Total: 7 actions
    assert len(actions) == 7

    # Group actions by value
    actions_by_value = {}
    for action in actions:
        if action.value not in actions_by_value:
            actions_by_value[action.value] = []
        actions_by_value[action.value].append(action)

    # Verify eliminations for value 1
    assert len(actions_by_value[1]) == 3
    cells_losing_1 = {a.cell for a in actions_by_value[1]}
    assert cells_losing_1 == {cell4, cell5, cell8}

    # Verify eliminations for value 5
    assert len(actions_by_value[5]) == 2
    cells_losing_5 = {a.cell for a in actions_by_value[5]}
    assert cells_losing_5 == {cell5, cell8}

    # Verify eliminations for value 9
    assert len(actions_by_value[9]) == 2
    cells_losing_9 = {a.cell for a in actions_by_value[9]}
    assert cells_losing_9 == {cell6, cell9}

    # Verify all actions have correct properties
    for action in actions:
        assert action.action == "remove_possible"
        assert action.value in {1, 5, 9}
        assert action.reason  # Just verify reason is not empty


def test_show_possibles_different_group_types():
    """Test that function works correctly for different group types"""
    field = Field("")

    cell1 = MockCell(position=CellPosition(3, 4), hopeful=set(), value=7)
    cell2 = MockCell(position=CellPosition(5, 6), hopeful={3, 7, 8})

    # Test row
    group = {cell1, cell2}
    actions = list(show_possibles(field, type="row", idx=4, group=group))
    assert len(actions) == 1
    assert actions[0].action == "remove_possible"
    assert actions[0].value == 7
    assert actions[0].cell == cell2

    # Test column
    actions = list(show_possibles(field, type="column", idx=2, group=group))
    assert len(actions) == 1
    assert actions[0].action == "remove_possible"
    assert actions[0].value == 7
    assert actions[0].cell == cell2

    # Test block
    actions = list(show_possibles(field, type="block", idx=5, group=group))
    assert len(actions) == 1
    assert actions[0].action == "remove_possible"
    assert actions[0].value == 7
    assert actions[0].cell == cell2


def test_show_possibles_with_real_cells():
    """Test with actual Cell objects instead of mock objects"""
    field = Field("")

    # Create real Cell objects
    cell1 = Cell(4, CellPosition(0, 0))  # Solved cell with value 4
    cell2 = Cell(0, CellPosition(1, 0))  # Unsolved cell
    cell3 = Cell(0, CellPosition(2, 0))  # Unsolved cell

    # Manually set hopeful values to simulate the solving state
    cell2.hopeful = {1, 4, 6, 7}  # Should lose 4
    cell3.hopeful = {2, 3, 5, 8}  # No 4, so no elimination

    group = {cell1, cell2, cell3}

    actions = list(show_possibles(field, type="row", idx=0, group=group))

    # Should generate 1 action: remove 4 from cell2
    assert len(actions) == 1

    action = actions[0]
    assert action.action == "remove_possible"
    assert action.value == 4
    assert action.cell == cell2
    assert action.reason  # Just verify reason is not empty


def test_show_possibles_duplicate_values_different_positions():
    """Test behavior when the same value appears in multiple solved cells (edge case)"""
    field = Field("")

    # This is an invalid Sudoku state but tests robustness
    cell1 = MockCell(position=CellPosition(0, 0), hopeful=set(), value=3)
    cell2 = MockCell(
        position=CellPosition(1, 0), hopeful=set(), value=3
    )  # Invalid: duplicate 3
    cell3 = MockCell(
        position=CellPosition(2, 0), hopeful={1, 3, 5}
    )  # Should lose 3 from both

    group = {cell1, cell2, cell3}

    actions = list(show_possibles(field, type="row", idx=0, group=group))

    # Should generate 2 actions: remove 3 from cell3 (once for each solved cell with value 3)
    assert len(actions) == 2

    for action in actions:
        assert action.action == "remove_possible"
        assert action.value == 3
        assert action.cell == cell3
        assert action.reason  # Just verify reason is not empty


def test_show_possibles_self_reference():
    """Test that a cell doesn't try to eliminate its own value from itself"""
    field = Field("")

    # A solved cell should not generate an action against itself
    cell1 = MockCell(position=CellPosition(0, 0), hopeful=set(), value=5)
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={1, 5, 9})

    group = {cell1, cell2}

    actions = list(show_possibles(field, type="row", idx=0, group=group))

    # Should generate 1 action: remove 5 from cell2 (not from cell1)
    assert len(actions) == 1

    action = actions[0]
    assert action.cell == cell2  # Not cell1
    assert action.value == 5


if __name__ == "__main__":
    pytest.main([__file__])
