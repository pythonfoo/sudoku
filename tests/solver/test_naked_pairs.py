from typing import NamedTuple

import pytest

from sudoku.action import Action
from sudoku.cell import Cell
from sudoku.field import Field
from sudoku.solver.naked_pairs import naked_pairs
from sudoku.types import CellPosition


class MockCell(NamedTuple):
    """Mock cell for testing purposes"""

    position: CellPosition
    hopeful: set[int]
    value: int = 0

    def __hash__(self) -> int:
        return self.position.as_int()


def test_naked_pairs_basic_elimination():
    """Test basic naked pair: two cells with same 2 values eliminate those values from others"""
    field = Field("")

    # Create a naked pair: cells 1 and 2 both have hopeful {3, 7}
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={3, 7})  # Part of naked pair
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={3, 7})  # Part of naked pair
    cell3 = MockCell(
        position=CellPosition(2, 0), hopeful={1, 3, 5, 7}
    )  # Should lose 3, 7
    cell4 = MockCell(position=CellPosition(3, 0), hopeful={2, 3, 6})  # Should lose 3
    cell5 = MockCell(position=CellPosition(4, 0), hopeful={1, 2, 4, 5})  # No 3 or 7

    group = {cell1, cell2, cell3, cell4, cell5}

    actions = list(naked_pairs(field, type="row", idx=0, group=group))

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
        assert action.value in {3, 7}
        assert action.reason  # Just verify reason is not empty


def test_naked_pairs_multiple_pairs():
    """Test multiple naked pairs in the same group"""
    field = Field("")

    # First naked pair: {1, 2}
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={1, 2})
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={1, 2})

    # Second naked pair: {8, 9}
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={8, 9})
    cell4 = MockCell(position=CellPosition(3, 0), hopeful={8, 9})

    # Cells that should be affected
    cell5 = MockCell(position=CellPosition(4, 0), hopeful={1, 3, 8})  # Should lose 1, 8
    cell6 = MockCell(position=CellPosition(5, 0), hopeful={2, 5, 9})  # Should lose 2, 9
    cell7 = MockCell(position=CellPosition(6, 0), hopeful={3, 4, 5})  # No eliminations

    group = {cell1, cell2, cell3, cell4, cell5, cell6, cell7}

    actions = list(naked_pairs(field, type="column", idx=0, group=group))

    # Should generate 4 actions: remove {1,8} from cell5, remove {2,9} from cell6
    assert len(actions) == 4

    # Group actions by target cell
    actions_by_cell = {}
    for action in actions:
        if action.cell not in actions_by_cell:
            actions_by_cell[action.cell] = []
        actions_by_cell[action.cell].append(action)

    # Verify eliminations for cell5
    assert len(actions_by_cell[cell5]) == 2
    values_removed_from_cell5 = {a.value for a in actions_by_cell[cell5]}
    assert values_removed_from_cell5 == {1, 8}

    # Verify eliminations for cell6
    assert len(actions_by_cell[cell6]) == 2
    values_removed_from_cell6 = {a.value for a in actions_by_cell[cell6]}
    assert values_removed_from_cell6 == {2, 9}

    # Verify cell7 has no eliminations
    assert cell7 not in actions_by_cell


def test_naked_pairs_no_pairs():
    """Test case where cells have 2 values but no matching pairs"""
    field = Field("")

    # All cells have 2 values, but no two cells have the same pair
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={1, 2})
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={3, 4})
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={5, 6})
    cell4 = MockCell(position=CellPosition(3, 0), hopeful={7, 8})

    group = {cell1, cell2, cell3, cell4}

    actions = list(naked_pairs(field, type="row", idx=0, group=group))

    # Should generate no actions since no pairs match
    assert len(actions) == 0


def test_naked_pairs_cells_with_different_hopeful_sizes():
    """Test mixed group with cells having different hopeful set sizes"""
    field = Field("")

    # Naked pair
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={4, 6})  # Pair member
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={4, 6})  # Pair member

    # Other cells with different hopeful sizes
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={1})  # Size 1
    cell4 = MockCell(
        position=CellPosition(3, 0), hopeful={2, 4, 6, 8}
    )  # Size 4, should lose 4,6
    cell5 = MockCell(
        position=CellPosition(4, 0), hopeful={3, 5, 7}
    )  # Size 3, no eliminations
    cell6 = MockCell(position=CellPosition(5, 0), hopeful=set())  # Empty (solved cell)

    group = {cell1, cell2, cell3, cell4, cell5, cell6}

    actions = list(naked_pairs(field, type="block", idx=0, group=group))

    # Should generate 2 actions: remove 4 and 6 from cell4
    assert len(actions) == 2

    values_removed = {a.value for a in actions}
    assert values_removed == {4, 6}

    # Both actions should target cell4
    for action in actions:
        assert action.cell == cell4


def test_naked_pairs_three_cells_same_pair():
    """Test case where 3 cells have the same 2-value hopeful set (not a valid naked pair)"""
    field = Field("")

    # Three cells with same hopeful set - this is not a naked pair
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={2, 8})
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={2, 8})
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={2, 8})
    cell4 = MockCell(
        position=CellPosition(3, 0), hopeful={1, 2, 8, 9}
    )  # Should not be affected

    group = {cell1, cell2, cell3, cell4}

    actions = list(naked_pairs(field, type="row", idx=0, group=group))

    # Should generate no actions since we need exactly 2 cells for a naked pair
    assert len(actions) == 0


def test_naked_pairs_empty_group():
    """Test with an empty group"""
    field = Field("")
    group = set()

    actions = list(naked_pairs(field, type="row", idx=0, group=group))

    # Should generate no actions
    assert len(actions) == 0


def test_naked_pairs_single_cell_group():
    """Test with a group containing only one cell"""
    field = Field("")

    cell1 = MockCell(position=CellPosition(0, 0), hopeful={1, 2})
    group = {cell1}

    actions = list(naked_pairs(field, type="column", idx=0, group=group))

    # Should generate no actions since naked pairs require at least 2 cells
    assert len(actions) == 0


def test_naked_pairs_no_cells_with_two_values():
    """Test case where no cells have exactly 2 hopeful values"""
    field = Field("")

    # No cells have exactly 2 values
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={1})  # Size 1
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={2, 3, 4})  # Size 3
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={5, 6, 7, 8})  # Size 4
    cell4 = MockCell(position=CellPosition(3, 0), hopeful=set())  # Empty

    group = {cell1, cell2, cell3, cell4}

    actions = list(naked_pairs(field, type="row", idx=0, group=group))

    # Should generate no actions since no cells have exactly 2 values
    assert len(actions) == 0


def test_naked_pairs_pair_affects_no_other_cells():
    """Test naked pair where no other cells contain the pair values"""
    field = Field("")

    # Naked pair
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={7, 9})
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={7, 9})

    # Other cells don't contain 7 or 9
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={1, 2, 3})
    cell4 = MockCell(position=CellPosition(3, 0), hopeful={4, 5, 6})
    cell5 = MockCell(position=CellPosition(4, 0), hopeful={8})

    group = {cell1, cell2, cell3, cell4, cell5}

    actions = list(naked_pairs(field, type="block", idx=0, group=group))

    # Should generate no actions since no other cells contain 7 or 9
    assert len(actions) == 0


def test_naked_pairs_complex_scenario():
    """Test a complex scenario with multiple interactions"""
    field = Field("")

    # First naked pair: {1, 5}
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={1, 5})
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={1, 5})

    # Second naked pair: {3, 8}
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={3, 8})
    cell4 = MockCell(position=CellPosition(3, 0), hopeful={3, 8})

    # Cells affected by both pairs
    cell5 = MockCell(
        position=CellPosition(4, 0), hopeful={1, 2, 3, 4}
    )  # Should lose 1, 3
    cell6 = MockCell(
        position=CellPosition(5, 0), hopeful={5, 6, 8, 9}
    )  # Should lose 5, 8

    # Cell affected by only one pair
    cell7 = MockCell(position=CellPosition(6, 0), hopeful={1, 6, 7})  # Should lose 1

    # Cell not affected
    cell8 = MockCell(
        position=CellPosition(7, 0), hopeful={2, 4, 6, 7}
    )  # No eliminations

    group = {cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8}

    actions = list(naked_pairs(field, type="row", idx=0, group=group))

    # Should generate 5 actions total
    # cell5 loses {1, 3} = 2 actions
    # cell6 loses {5, 8} = 2 actions
    # cell7 loses {1} = 1 action
    assert len(actions) == 5

    # Group actions by target cell
    actions_by_cell = {}
    for action in actions:
        if action.cell not in actions_by_cell:
            actions_by_cell[action.cell] = []
        actions_by_cell[action.cell].append(action)

    # Verify eliminations
    assert len(actions_by_cell[cell5]) == 2
    values_from_cell5 = {a.value for a in actions_by_cell[cell5]}
    assert values_from_cell5 == {1, 3}

    assert len(actions_by_cell[cell6]) == 2
    values_from_cell6 = {a.value for a in actions_by_cell[cell6]}
    assert values_from_cell6 == {5, 8}

    assert len(actions_by_cell[cell7]) == 1
    assert actions_by_cell[cell7][0].value == 1

    # cell8 should not be affected
    assert cell8 not in actions_by_cell


def test_naked_pairs_with_real_cells():
    """Test with actual Cell objects instead of mock objects"""
    field = Field("")

    # Create real Cell objects
    cell1 = Cell(0, CellPosition(0, 0))
    cell2 = Cell(0, CellPosition(1, 0))
    cell3 = Cell(0, CellPosition(2, 0))

    # Manually set hopeful values to create a naked pair
    cell1.hopeful = {2, 6}  # Part of naked pair
    cell2.hopeful = {2, 6}  # Part of naked pair
    cell3.hopeful = {1, 2, 4, 6, 7}  # Should lose 2 and 6

    group = {cell1, cell2, cell3}

    actions = list(naked_pairs(field, type="column", idx=0, group=group))

    # Should generate 2 actions: remove 2 and 6 from cell3
    assert len(actions) == 2

    values_removed = {a.value for a in actions}
    assert values_removed == {2, 6}

    # Both actions should target cell3
    for action in actions:
        assert action.action == "remove_possible"
        assert action.cell == cell3
        assert action.reason  # Just verify reason is not empty


def test_naked_pairs_different_group_types():
    """Test that function works correctly for different group types"""
    field = Field("")

    # Create a naked pair
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={4, 9})
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={4, 9})
    cell3 = MockCell(position=CellPosition(2, 0), hopeful={1, 4, 9})

    group = {cell1, cell2, cell3}

    # Test with different group types - behavior should be the same
    for group_type in ["row", "column", "block"]:
        actions = list(naked_pairs(field, type=group_type, idx=0, group=group))

        assert len(actions) == 2
        values_removed = {a.value for a in actions}
        assert values_removed == {4, 9}

        for action in actions:
            assert action.action == "remove_possible"
            assert action.cell == cell3


def test_naked_pairs_self_exclusion():
    """Test that naked pair members don't eliminate values from themselves"""
    field = Field("")

    # Create naked pair
    cell1 = MockCell(position=CellPosition(0, 0), hopeful={3, 5})
    cell2 = MockCell(position=CellPosition(1, 0), hopeful={3, 5})

    group = {cell1, cell2}

    actions = list(naked_pairs(field, type="row", idx=0, group=group))

    # Should generate no actions since the naked pair members shouldn't
    # eliminate values from themselves, and there are no other cells
    assert len(actions) == 0


if __name__ == "__main__":
    pytest.main([__file__])
