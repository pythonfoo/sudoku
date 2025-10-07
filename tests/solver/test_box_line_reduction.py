import pytest

from sudoku.field import Field
from sudoku.solver.box_line_reduction import box_line_reduction


def _set_all_cells_hopeful(field: Field, hopeful_set: set[int]) -> None:
    """Helper to set the hopeful set for every cell in a field."""
    for cell in field.cells:
        cell.hopeful = set(hopeful_set)


def test_box_line_reduction_basic_row_elimination():
    """
    Basic scenario:
    - In row 0, the candidate `5` appears only in two cells that both belong to block 1.
    - Another cell inside block 1 (but not in the row) contains `5` in its hopeful set.
    -> box_line_reduction should produce a single action removing `5` from that other block cell.
    """
    field = Field("0" * 81)  # full empty field (81 cells)

    # Make a clean baseline: no cell contains 5 initially
    _set_all_cells_hopeful(field, {1, 2, 3})

    # Target row and block:
    # row 0 has coordinates y = 0
    # choose two cells in row 0 that are inside block 1 (x in 3..5)
    member_a = field.get_cell(3, 0)
    member_b = field.get_cell(4, 0)
    member_a.hopeful.add(5)
    member_b.hopeful.add(5)

    # Add another cell inside the same block (block 1) but not in the row,
    # which should be affected by the rule.
    victim = field.get_cell(5, 1)  # x=5,y=1 is in block1 but not in row0
    victim.hopeful.add(5)

    group = field.get_group("row", 0)
    actions = list(box_line_reduction(field, type="row", idx=0, group=group))

    assert len(actions) == 1, "Expected exactly one elimination action"
    action = actions[0]
    assert action.action == "remove_possible"
    assert action.value == 5
    assert action.cell is victim
    # Reason should mention the box id (1)
    assert "only in box 1" in action.reason


def test_box_line_reduction_multiple_values_and_columns():
    """
    More advanced scenario:
    - In row 4 we create two different candidates that are each confined to a single block
      (one confined to block 3, the other confined to block 5).
    - Each confined candidate has at least one other cell in its block (outside the row)
      that contains that candidate -> both should be eliminated.
    """
    field = Field("0" * 81)
    _set_all_cells_hopeful(field, {1, 3})  # baseline not including 2 or 9

    # Row 4 (y = 4)
    # Candidate 2 confined to block 3 (left middle block).
    # Cells in row 4 inside block 3 are x=0..2 (pick two)
    b3_member1 = field.get_cell(0, 4)
    b3_member2 = field.get_cell(1, 4)
    b3_member1.hopeful.add(2)
    b3_member2.hopeful.add(2)
    # Another cell in block 3 but not in row 4 should lose 2
    b3_victim = field.get_cell(2, 3)  # still in block 3
    b3_victim.hopeful.add(2)

    # Candidate 9 confined to block 5 (right middle block).
    # Cells in row 4 inside block 5 are x=6..8 (pick two)
    b5_member1 = field.get_cell(6, 4)
    b5_member2 = field.get_cell(7, 4)
    b5_member1.hopeful.add(9)
    b5_member2.hopeful.add(9)
    # Another cell in block 5 but not in row 4 should lose 9
    b5_victim = field.get_cell(8, 5)
    b5_victim.hopeful.add(9)

    group = field.get_group("row", 4)
    actions = list(box_line_reduction(field, type="row", idx=4, group=group))

    # We expect two eliminations: one removing 2 from b3_victim, one removing 9 from b5_victim
    assert len(actions) == 2

    # Map (cell -> set(values removed))
    removals = {}
    for a in actions:
        assert a.action == "remove_possible"
        removals.setdefault(a.cell, set()).add(a.value)

    assert removals.get(b3_victim) == {2}
    assert removals.get(b5_victim) == {9}

    # Ensure we did not accidentally remove from the members themselves
    assert b3_member1 not in removals
    assert b3_member2 not in removals
    assert b5_member1 not in removals
    assert b5_member2 not in removals


def test_box_line_reduction_no_action_when_spread_across_blocks():
    """
    If a candidate appears in the checked group but its occurrences are spread over
    multiple blocks, no block-line reduction should be performed for that candidate,
    even if the block contains other cells with that candidate.
    """
    field = Field("0" * 81)
    _set_all_cells_hopeful(field, {1, 4})  # baseline not including 6

    # Row 1 (y = 1)
    # Place candidate 6 in two cells that are located in different blocks:
    # - (1,1) is block 0
    # - (4,1) is block 1
    spread_a = field.get_cell(1, 1)
    spread_b = field.get_cell(4, 1)
    spread_a.hopeful.add(6)
    spread_b.hopeful.add(6)

    # Also place 6 in some cells inside block 0 and block 1 to ensure that
    # if the rule were applied incorrectly it would remove them.
    block0_victim = field.get_cell(2, 0)
    block0_victim.hopeful.add(6)
    block1_victim = field.get_cell(3, 2)
    block1_victim.hopeful.add(6)

    group = field.get_group("row", 1)
    actions = list(box_line_reduction(field, type="row", idx=1, group=group))

    # No actions expected because the occurrences of 6 in the row are not confined to a single block
    assert len(actions) == 0


if __name__ == "__main__":
    pytest.main([__file__])
