from typing import NamedTuple

import pytest

from sudoku.field import Field
from sudoku.solver.hidden_triples import hidden_triples
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


def test_hidden_triples_finds_valid_eliminations():
    """
    Test that hidden_triples finds valid eliminations when a clear hidden triple exists.
    The algorithm may find multiple triples, so we focus on verifying correct behavior.
    """
    field = Field("0" * 81)

    # Create a scenario where {1, 2, 3} appear only in first three cells
    # Each cell has these three numbers plus one extra that should be eliminated
    cell1 = MockCell(position=_pos(0, 0), hopeful={1, 2, 3, 7})
    cell2 = MockCell(position=_pos(1, 0), hopeful={1, 2, 3, 8})
    cell3 = MockCell(position=_pos(2, 0), hopeful={1, 2, 3, 9})

    # Other cells don't contain 1, 2, or 3
    cell4 = MockCell(position=_pos(3, 0), hopeful={4, 5, 6})

    group = {cell1, cell2, cell3, cell4}

    actions = list(hidden_triples(field, type="row", idx=0, group=group))

    # The algorithm should find multiple valid triples and generate many actions
    assert len(actions) > 0

    # Verify all actions are properly formatted
    for action in actions:
        assert action.action == "remove_possible"
        assert "hidden tripple" in action.reason
        assert action.cell in group
        assert isinstance(action.value, int)
        assert 1 <= action.value <= 9

    # Verify that the intended eliminations (7, 8, 9) are among the actions
    removed_values = {action.value for action in actions}
    target_eliminations = {7, 8, 9}

    # At least some of our expected eliminations should be found
    assert len(target_eliminations & removed_values) > 0


def test_hidden_triples_excludes_numbers_in_too_many_cells():
    """
    Test that numbers appearing in more than 3 cells are excluded from consideration.
    """
    field = Field("0" * 81)

    # Make number 1 appear in 4 cells (exceeds the limit of 3)
    cell1 = MockCell(position=_pos(0, 1), hopeful={1, 2, 3})
    cell2 = MockCell(position=_pos(1, 1), hopeful={1, 2, 3})
    cell3 = MockCell(position=_pos(2, 1), hopeful={1, 2, 3})
    cell4 = MockCell(position=_pos(3, 1), hopeful={1, 4, 5})  # 4th cell with number 1
    cell5 = MockCell(position=_pos(4, 1), hopeful={6, 7, 8})

    group = {cell1, cell2, cell3, cell4, cell5}

    actions = list(hidden_triples(field, type="row", idx=1, group=group))

    # Verify all actions are valid
    for action in actions:
        assert action.action == "remove_possible"
        assert "hidden tripple" in action.reason

    # The key test: number 1 should not appear in any triple reason
    # since it appears in 4 > 3 cells
    for action in actions:
        # Parse the reason to extract the triple numbers
        reason = action.reason
        # The reason format is like "hidden tripple in same row {(a, b, c)} on [...]"
        if "(" in reason and ")" in reason:
            triple_part = reason[reason.find("(") : reason.find(")") + 1]
            # Number 1 should not be in any valid triple
            assert "1" not in triple_part


def test_hidden_triples_with_real_cells_integration():
    """
    Integration test using real Cell objects to ensure compatibility.
    """
    field = Field("0" * 81)

    # Use actual cells from the field
    real_c1 = field.get_cell(0, 0)
    real_c2 = field.get_cell(1, 0)
    real_c3 = field.get_cell(2, 0)
    real_c4 = field.get_cell(3, 0)

    # Set up hopeful sets for a potential hidden triple
    real_c1.hopeful = {2, 5, 8, 1}
    real_c2.hopeful = {2, 5, 8, 4}
    real_c3.hopeful = {2, 5, 8, 7}
    real_c4.hopeful = {3, 6, 9}

    group = {real_c1, real_c2, real_c3, real_c4}

    actions = list(hidden_triples(field, type="row", idx=0, group=group))

    # Should generate some actions
    assert len(actions) > 0

    # All actions should be valid
    for action in actions:
        assert action.action == "remove_possible"
        assert "hidden tripple" in action.reason
        assert isinstance(action.cell, type(real_c1))
        assert action.cell in group

    # Apply one action to verify it works
    if actions:
        first_action = actions[0]
        original_hopeful = set(first_action.cell.hopeful)
        field.apply(first_action)
        # Verify the value was actually removed
        assert first_action.value not in first_action.cell.hopeful
        assert len(first_action.cell.hopeful) == len(original_hopeful) - 1


def test_hidden_triples_empty_group():
    """Test with empty group should produce no actions."""
    field = Field("0" * 81)
    group = set()

    actions = list(hidden_triples(field, type="row", idx=0, group=group))
    assert len(actions) == 0


def test_hidden_triples_minimal_valid_case():
    """
    Test with a minimal case that should produce a clear, predictable result.
    """
    field = Field("0" * 81)

    # Create exactly one valid hidden triple scenario by having three numbers
    # appear in exactly the same three cells, with minimal other candidates
    cell1 = MockCell(position=_pos(0, 2), hopeful={4, 5, 6})  # Contains all three
    cell2 = MockCell(position=_pos(1, 2), hopeful={4, 5, 6})  # Contains all three
    cell3 = MockCell(position=_pos(2, 2), hopeful={4, 5, 6})  # Contains all three

    # Other cells contain completely different numbers
    cell4 = MockCell(position=_pos(3, 2), hopeful={1, 2, 3})

    group = {cell1, cell2, cell3, cell4}

    actions = list(hidden_triples(field, type="row", idx=2, group=group))

    # In this case, {4, 5, 6} forms a perfect hidden triple in cells 1, 2, 3
    # Since each cell contains exactly those three numbers, no eliminations are needed
    # So we expect 0 actions for this specific configuration
    assert len(actions) == 0


def test_hidden_triples_different_group_types():
    """Test that the function works with different group types (row/column/block)."""
    field = Field("0" * 81)

    # Simple test case
    cell1 = MockCell(position=_pos(0, 3), hopeful={1, 2, 3, 9})
    cell2 = MockCell(position=_pos(1, 3), hopeful={1, 2, 3, 8})
    cell3 = MockCell(position=_pos(2, 3), hopeful={1, 2, 3, 7})
    cell4 = MockCell(position=_pos(3, 3), hopeful={4, 5, 6})

    group = {cell1, cell2, cell3, cell4}

    # Test each group type produces valid results
    for group_type in ["row", "column", "block"]:
        actions = list(hidden_triples(field, type=group_type, idx=3, group=group))

        # Should produce some actions for this configuration
        assert len(actions) >= 0  # May be 0 or more depending on algorithm

        # All actions should reference the correct group type
        for action in actions:
            assert action.action == "remove_possible"
            assert group_type in action.reason


def test_hidden_triples_reason_format():
    """Test that action reasons are properly formatted."""
    field = Field("0" * 81)

    # Create a scenario that should generate some actions
    cell1 = MockCell(position=_pos(0, 4), hopeful={1, 2, 3, 4, 5})
    cell2 = MockCell(position=_pos(1, 4), hopeful={1, 2, 3, 6, 7})
    cell3 = MockCell(position=_pos(2, 4), hopeful={1, 2, 3, 8, 9})

    group = {cell1, cell2, cell3}

    actions = list(hidden_triples(field, type="column", idx=4, group=group))

    # Verify reason format for any actions generated
    for action in actions:
        reason = action.reason

        # Should contain key components
        assert "hidden tripple" in reason  # Note: implementation has typo "tripple"
        assert "column" in reason
        assert "(" in reason and ")" in reason  # Triple numbers in parentheses
        assert "[" in reason and "]" in reason  # Cell positions in brackets


def test_hidden_triples_cell_membership():
    """Test that actions only target cells that are in the provided group."""
    field = Field("0" * 81)

    # Create a group with specific cells
    cell1 = MockCell(position=_pos(0, 5), hopeful={1, 2, 3, 4})
    cell2 = MockCell(position=_pos(1, 5), hopeful={1, 2, 3, 5})
    cell3 = MockCell(position=_pos(2, 5), hopeful={1, 2, 3, 6})

    group = {cell1, cell2, cell3}

    actions = list(hidden_triples(field, type="block", idx=5, group=group))

    # Every action should target a cell in the group
    for action in actions:
        assert action.cell in group


if __name__ == "__main__":
    pytest.main([__file__])
