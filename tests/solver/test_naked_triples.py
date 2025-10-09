from typing import NamedTuple

import pytest

from sudoku.cell import Cell
from sudoku.field import Field
from sudoku.solver.naked_triples import naked_triples
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


def test_naked_triples_basic_3_3_3_formation():
    """
    Test basic naked triple with {3/3/3} formation:
    Three cells each containing the same three candidates.
    """
    field = Field("0" * 81)

    # Three cells forming a naked triple {1, 2, 3}
    cell1 = MockCell(position=_pos(0, 0), hopeful={1, 2, 3})
    cell2 = MockCell(position=_pos(1, 0), hopeful={1, 2, 3})
    cell3 = MockCell(position=_pos(2, 0), hopeful={1, 2, 3})

    # Other cells that should have 1, 2, 3 removed
    cell4 = MockCell(position=_pos(3, 0), hopeful={1, 4, 5, 6})  # Should lose 1
    cell5 = MockCell(position=_pos(4, 0), hopeful={2, 7, 8})  # Should lose 2
    cell6 = MockCell(position=_pos(5, 0), hopeful={3, 4, 7})  # Should lose 3

    group = {cell1, cell2, cell3, cell4, cell5, cell6}

    actions = list(naked_triples(field, type="row", idx=0, group=group))

    # Should remove 1, 2, 3 from other cells
    assert len(actions) == 3

    actions_by_value = {}
    for action in actions:
        assert action.action == "remove_possible"
        assert "naked triple" in action.reason
        assert action.value in {1, 2, 3}
        actions_by_value[action.value] = action.cell

    assert actions_by_value[1] == cell4
    assert actions_by_value[2] == cell5
    assert actions_by_value[3] == cell6


def test_naked_triples_3_3_2_formation():
    """
    Test naked triple with {3/3/2} formation:
    Two cells with all three candidates, one cell with two candidates.
    """
    field = Field("0" * 81)

    # Naked triple {4, 5, 6} in different formations
    cell1 = MockCell(position=_pos(0, 1), hopeful={4, 5, 6})  # Has all three
    cell2 = MockCell(position=_pos(1, 1), hopeful={4, 5, 6})  # Has all three
    cell3 = MockCell(position=_pos(2, 1), hopeful={4, 5})  # Has only two

    # Other cells that should be affected
    cell4 = MockCell(position=_pos(3, 1), hopeful={4, 7, 8})  # Should lose 4
    cell5 = MockCell(position=_pos(4, 1), hopeful={5, 6, 1})  # Should lose 5, 6

    group = {cell1, cell2, cell3, cell4, cell5}

    actions = list(naked_triples(field, type="row", idx=1, group=group))

    # Should remove 4, 5, 6 from other cells
    assert len(actions) == 3

    removed_values = {action.value for action in actions}
    assert removed_values == {4, 5, 6}

    # Verify correct cells are targeted
    actions_by_value = {}
    for action in actions:
        actions_by_value[action.value] = action.cell

    assert actions_by_value[4] == cell4
    assert actions_by_value[5] == cell5
    assert actions_by_value[6] == cell5


def test_naked_triples_3_2_2_formation():
    """
    Test naked triple with {3/2/2} formation where the algorithm can find
    the triple by extending 2-candidate cells.
    Note: Algorithm only extends with values 1-8, not 9.
    """
    field = Field("0" * 81)

    # Naked triple {1, 7, 8} - specifically avoiding 9 due to algorithm limitation
    cell1 = MockCell(position=_pos(0, 2), hopeful={1, 7, 8})  # Has all three
    cell2 = MockCell(
        position=_pos(1, 2), hopeful={7, 8}
    )  # Has two (will extend with 1)
    cell3 = MockCell(
        position=_pos(2, 2), hopeful={1, 8}
    )  # Has two (will extend with 7)

    # Cells that should be affected
    cell4 = MockCell(position=_pos(3, 2), hopeful={1, 2, 3})  # Should lose 1
    cell5 = MockCell(position=_pos(4, 2), hopeful={7, 4, 5})  # Should lose 7
    cell6 = MockCell(position=_pos(5, 2), hopeful={8, 6})  # Should lose 8

    group = {cell1, cell2, cell3, cell4, cell5, cell6}

    actions = list(naked_triples(field, type="column", idx=2, group=group))

    # Should remove 1, 7, 8 from other cells
    assert len(actions) == 3

    actions_by_value = {}
    for action in actions:
        assert action.action == "remove_possible"
        assert "naked triple" in action.reason
        assert "column" in action.reason
        actions_by_value[action.value] = action.cell

    assert actions_by_value[1] == cell4
    assert actions_by_value[7] == cell5
    assert actions_by_value[8] == cell6


def test_naked_triples_2_2_2_formation():
    """
    Test naked triple with {2/2/2} formation (Y-Wing pattern):
    Three cells each with two candidates, forming a triangle pattern.
    """
    field = Field("0" * 81)

    # Y-Wing naked triple pattern {1, 3, 5}
    cell1 = MockCell(position=_pos(0, 3), hopeful={1, 3})  # 13
    cell2 = MockCell(position=_pos(1, 3), hopeful={3, 5})  # 35
    cell3 = MockCell(position=_pos(2, 3), hopeful={1, 5})  # 15

    # Other cells that should be affected
    cell4 = MockCell(position=_pos(3, 3), hopeful={1, 2, 4})  # Should lose 1
    cell5 = MockCell(position=_pos(4, 3), hopeful={3, 6, 7})  # Should lose 3
    cell6 = MockCell(position=_pos(5, 3), hopeful={5, 8})  # Should lose 5

    group = {cell1, cell2, cell3, cell4, cell5, cell6}

    actions = list(naked_triples(field, type="block", idx=3, group=group))

    assert len(actions) == 3

    actions_by_value = {}
    for action in actions:
        assert action.action == "remove_possible"
        assert "naked triple" in action.reason
        assert "block" in action.reason
        actions_by_value[action.value] = action.cell

    assert actions_by_value[1] == cell4
    assert actions_by_value[3] == cell5
    assert actions_by_value[5] == cell6


def test_naked_triples_no_action_when_insufficient_cells():
    """
    Test that no actions are generated when there aren't exactly 3 cells
    forming the naked triple pattern.
    """
    field = Field("0" * 81)

    # Only two cells with the same candidates - not enough for a triple
    cell1 = MockCell(position=_pos(0, 4), hopeful={1, 2, 3})
    cell2 = MockCell(position=_pos(1, 4), hopeful={1, 2, 3})
    cell3 = MockCell(position=_pos(2, 4), hopeful={4, 5, 6})  # Different candidates

    group = {cell1, cell2, cell3}

    actions = list(naked_triples(field, type="row", idx=4, group=group))

    # Should not find a naked triple
    assert len(actions) == 0


def test_naked_triples_no_action_when_no_eliminations_needed():
    """
    Test case where a naked triple exists but no other cells contain
    the triple values, so no eliminations are needed.
    """
    field = Field("0" * 81)

    # Naked triple exists
    cell1 = MockCell(position=_pos(0, 5), hopeful={2, 4, 6})
    cell2 = MockCell(position=_pos(1, 5), hopeful={2, 4, 6})
    cell3 = MockCell(position=_pos(2, 5), hopeful={2, 4})

    # Other cells don't contain any of {2, 4, 6}
    cell4 = MockCell(position=_pos(3, 5), hopeful={1, 3, 5})
    cell5 = MockCell(position=_pos(4, 5), hopeful={7, 8})

    group = {cell1, cell2, cell3, cell4, cell5}

    actions = list(naked_triples(field, type="row", idx=5, group=group))

    # No eliminations needed
    assert len(actions) == 0


def test_naked_triples_extension_logic():
    """
    Test the algorithm's extension logic: cells with 2 candidates are extended
    by trying each missing value from 1-8 (note: not 9).
    """
    field = Field("0" * 81)

    # Create cells where extension logic is needed
    cell1 = MockCell(position=_pos(0, 6), hopeful={1, 2, 3})  # Complete triple
    cell2 = MockCell(position=_pos(1, 6), hopeful={1, 2})  # Extends to {1, 2, 3}
    cell3 = MockCell(position=_pos(2, 6), hopeful={2, 3})  # Extends to {1, 2, 3}

    # Cell that should be affected
    cell4 = MockCell(position=_pos(3, 6), hopeful={1, 4, 5})  # Should lose 1

    group = {cell1, cell2, cell3, cell4}

    actions = list(naked_triples(field, type="row", idx=6, group=group))

    # Should find the {1, 2, 3} triple through extension
    assert len(actions) >= 1

    # Verify that 1 is removed from cell4
    removed_values = {action.value for action in actions if action.cell == cell4}
    assert 1 in removed_values


def test_naked_triples_ignores_cells_with_more_than_three_candidates():
    """
    Test that cells with more than 3 candidates are ignored for forming triples
    but can still be targets for elimination.
    """
    field = Field("0" * 81)

    # Naked triple
    cell1 = MockCell(position=_pos(0, 7), hopeful={2, 6, 7})
    cell2 = MockCell(position=_pos(1, 7), hopeful={2, 6, 7})
    cell3 = MockCell(position=_pos(2, 7), hopeful={2, 6})

    # Cell with >3 candidates - ignored for triple formation but can be affected
    cell4 = MockCell(position=_pos(3, 7), hopeful={2, 3, 4, 5, 8})  # Should lose 2

    # Cell with >3 candidates - not affected
    cell5 = MockCell(position=_pos(4, 7), hopeful={1, 3, 4, 5, 8})

    group = {cell1, cell2, cell3, cell4, cell5}

    actions = list(naked_triples(field, type="block", idx=7, group=group))

    # Should find eliminations from the triple
    assert len(actions) >= 1

    # Verify cell4 loses the value 2
    cell4_actions = [a for a in actions if a.cell == cell4]
    assert len(cell4_actions) >= 1
    assert 2 in {a.value for a in cell4_actions}

    # Verify cell5 is not affected
    cell5_actions = [a for a in actions if a.cell == cell5]
    assert len(cell5_actions) == 0


def test_naked_triples_with_real_cells():
    """
    Integration test using real Cell objects from Field.
    """
    field = Field("0" * 81)

    # Use real cells from the field
    real_c1 = field.get_cell(0, 0)
    real_c2 = field.get_cell(1, 0)
    real_c3 = field.get_cell(2, 0)
    real_c4 = field.get_cell(3, 0)

    # Set up a naked triple {3, 6, 7} (avoiding 8,9 due to algorithm limitation)
    real_c1.hopeful = {3, 6, 7}
    real_c2.hopeful = {3, 6, 7}
    real_c3.hopeful = {3, 6}
    real_c4.hopeful = {3, 4, 5}  # Should lose 3

    group = {real_c1, real_c2, real_c3, real_c4}

    actions = list(naked_triples(field, type="row", idx=0, group=group))

    assert len(actions) == 1
    action = actions[0]

    assert action.action == "remove_possible"
    assert action.value == 3
    assert action.cell == real_c4
    assert "naked triple" in action.reason

    # Apply the action and verify it works
    original_hopeful = set(real_c4.hopeful)
    field.apply(action)

    assert 3 not in real_c4.hopeful
    assert len(real_c4.hopeful) == len(original_hopeful) - 1


def test_naked_triples_algorithm_range_limitation():
    """
    Test that demonstrates the algorithm's limitation: it only extends
    2-candidate cells with values 1-8, not 9.

    Note: The current implementation will try to extend 2-candidate cells
    by each missing value from 1-8. That means it may still form an alternate
    triple (for example (1,7,8)) and therefore produce eliminations for
    value 1 on `cell4`. What it must not do is remove 9, because 9 is never
    used in the extension loop. This test asserts that behavior.
    """
    field = Field("0" * 81)

    # Try to create a triple that would require using 9 to extend, which the
    # algorithm does not attempt. The three 2-candidate cells could still be
    # extended with other values (1-8), producing a different triple.
    cell1 = MockCell(position=_pos(0, 8), hopeful={1, 8})
    cell2 = MockCell(position=_pos(1, 8), hopeful={1, 8})
    cell3 = MockCell(position=_pos(2, 8), hopeful={1, 8})

    # Cell that might be affected if algorithm formed a triple without 9
    cell4 = MockCell(position=_pos(3, 8), hopeful={1, 9})

    group = {cell1, cell2, cell3, cell4}

    actions = list(naked_triples(field, type="row", idx=8, group=group))

    # The implementation does not try extending with 9; it tries 1-8.
    # Therefore it may produce eliminations for 1 on cell4 (via an alternate triple),
    # but it should never remove 9. Assert that if any removal from cell4
    # happens, 1 is among them, and that 9 is never removed by this solver.
    removed_from_cell4 = {a.value for a in actions if a.cell == cell4}
    assert (len(actions) == 0 and len(removed_from_cell4) == 0) or (
        1 in removed_from_cell4
    )

    # Ensure 9 is not removed by this solver
    assert 9 not in {a.value for a in actions}


def test_naked_triples_different_group_types():
    """
    Test that naked triples work correctly for different group types.
    """
    field = Field("0" * 81)

    # Same naked triple pattern
    cell1 = MockCell(position=_pos(4, 4), hopeful={4, 7, 8})
    cell2 = MockCell(position=_pos(4, 5), hopeful={4, 7, 8})
    cell3 = MockCell(position=_pos(4, 6), hopeful={4, 7})
    cell4 = MockCell(position=_pos(4, 7), hopeful={4, 1, 2})  # Should lose 4

    group = {cell1, cell2, cell3, cell4}

    # Test with different group types
    for group_type in ["row", "column", "block"]:
        actions = list(naked_triples(field, type=group_type, idx=4, group=group))

        # Should find eliminations regardless of group type
        assert len(actions) >= 1

        for action in actions:
            assert action.action == "remove_possible"
            assert group_type in action.reason
            assert "naked triple" in action.reason


def test_naked_triples_empty_group():
    """Test with empty group should produce no actions."""
    field = Field("0" * 81)
    group = set()

    actions = list(naked_triples(field, type="row", idx=0, group=group))
    assert len(actions) == 0


def test_naked_triples_single_cell_group():
    """Test with single cell group should produce no actions."""
    field = Field("0" * 81)

    cell1 = MockCell(position=_pos(0, 0), hopeful={1, 2, 3})
    group = {cell1}

    actions = list(naked_triples(field, type="row", idx=0, group=group))
    assert len(actions) == 0


def test_naked_triples_reason_format():
    """Test that action reasons are properly formatted."""
    field = Field("0" * 81)

    # Set up a clear naked triple scenario
    cell1 = MockCell(position=_pos(0, 1), hopeful={5, 6, 7})
    cell2 = MockCell(position=_pos(1, 1), hopeful={5, 6})
    cell3 = MockCell(position=_pos(2, 1), hopeful={6, 7})
    cell4 = MockCell(position=_pos(3, 1), hopeful={5, 1, 2})  # Should lose 5

    group = {cell1, cell2, cell3, cell4}

    actions = list(naked_triples(field, type="column", idx=1, group=group))

    assert len(actions) >= 1

    for action in actions:
        reason = action.reason

        # Verify reason format
        assert "naked triple" in reason
        assert "column" in reason
        assert "(" in reason and ")" in reason  # Triple tuple in parentheses
        assert "[" in reason and "]" in reason  # Cell positions in brackets

        # Verify the triple tuple is properly formatted
        assert "(5, 6, 7)" in reason


def test_naked_triples_multiple_valid_triples():
    """
    Test scenario where multiple naked triples could exist in the same group.
    """
    field = Field("0" * 81)

    # First triple {1, 2, 3}
    cell1 = MockCell(position=_pos(0, 0), hopeful={1, 2, 3})
    cell2 = MockCell(position=_pos(1, 0), hopeful={1, 2, 3})
    cell3 = MockCell(position=_pos(2, 0), hopeful={1, 2})

    # Second triple {4, 5, 6}
    cell4 = MockCell(position=_pos(3, 0), hopeful={4, 5, 6})
    cell5 = MockCell(position=_pos(4, 0), hopeful={4, 5, 6})
    cell6 = MockCell(position=_pos(5, 0), hopeful={4, 5})

    # Cell affected by both triples
    cell7 = MockCell(position=_pos(6, 0), hopeful={1, 4, 7, 8})  # Should lose 1, 4

    group = {cell1, cell2, cell3, cell4, cell5, cell6, cell7}

    actions = list(naked_triples(field, type="row", idx=0, group=group))

    # Should find eliminations from both triples
    assert len(actions) >= 2

    removed_values = {action.value for action in actions if action.cell == cell7}
    assert 1 in removed_values
    assert 4 in removed_values


if __name__ == "__main__":
    pytest.main([__file__])
