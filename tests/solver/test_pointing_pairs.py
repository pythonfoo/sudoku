import pytest

from sudoku.field import Field
from sudoku.solver.pointing_pairs import pointing_pairs


def _set_all_cells_hopeful(field: Field, hopeful_set: set[int]) -> None:
    """Helper to set the hopeful set for every cell in a field."""
    for cell in field.cells:
        cell.hopeful = set(hopeful_set)


def test_pointing_pairs_basic_row_pointing():
    """
    Basic scenario:
    - Inside block 1 (top-middle block) place candidate `5` in two cells that
      are both on the same row (y == 0).
    - Place the same candidate in another cell on that row but outside the block.
    -> pointing_pairs should remove `5` from the outside-row cell.
    """
    field = Field("0" * 81)
    _set_all_cells_hopeful(field, {1, 2, 3})

    # Block 1 covers x=3..5, y=0..2. Put two occurrences of 5 in row 0 inside block 1.
    in_block_a = field.get_cell(3, 0)
    in_block_b = field.get_cell(4, 0)
    in_block_a.hopeful.add(5)
    in_block_b.hopeful.add(5)

    # Outside the block but in the same row (row 0), place 5 so it should be eliminated.
    outside_row_victim = field.get_cell(2, 0)  # x=2,y=0 is in block 0 (not block 1)
    outside_row_victim.hopeful.add(5)

    group = field.get_group("block", 1)
    actions = list(pointing_pairs(field, type="block", idx=1, group=group))

    assert len(actions) == 1
    action = actions[0]
    assert action.action == "remove_possible"
    assert action.value == 5
    assert action.cell is outside_row_victim
    assert "pointing pair" in action.reason
    assert "row" in action.reason


def test_pointing_pairs_basic_column_pointing():
    """
    Basic column pointing:
    - Inside a block place candidate `7` in two cells that share the same column.
    - Place the candidate elsewhere in that column outside the block -> should be removed.
    """
    field = Field("0" * 81)
    _set_all_cells_hopeful(field, {1, 2, 3})

    # Choose block 1 (x=3..5, y=0..2).
    # Put two occurrences of 7 in the same column x=3 inside the block.
    in_block_a = field.get_cell(3, 0)
    in_block_b = field.get_cell(3, 1)
    in_block_a.hopeful.add(7)
    in_block_b.hopeful.add(7)

    # Place 7 in the same column but outside the block
    outside_col_victim = field.get_cell(3, 4)  # y=4 outside block 1
    outside_col_victim.hopeful.add(7)

    group = field.get_group("block", 1)
    actions = list(pointing_pairs(field, type="block", idx=1, group=group))

    assert len(actions) == 1
    action = actions[0]
    assert action.action == "remove_possible"
    assert action.value == 7
    assert action.cell is outside_col_victim
    assert "pointing pair" in action.reason
    assert "column" in action.reason


def test_pointing_pairs_no_action_when_spread_within_block():
    """
    If the candidate occurrences inside the block are spread across multiple rows
    and columns (i.e. not confined to a single row or single column), no action
    should be produced.
    """
    field = Field("0" * 81)
    _set_all_cells_hopeful(field, {1, 2, 3})

    # In block 1, put candidate 6 in two cells that are in different rows
    a = field.get_cell(3, 0)  # row 0
    b = field.get_cell(4, 1)  # row 1
    a.hopeful.add(6)
    b.hopeful.add(6)

    # Put 6 elsewhere in the row/column to make sure an incorrect implementation
    # would attempt to remove it; correct implementation must not.
    potential_victim = field.get_cell(2, 0)
    potential_victim.hopeful.add(6)

    group = field.get_group("block", 1)
    actions = list(pointing_pairs(field, type="block", idx=1, group=group))

    # No actions expected because occurrences in the block are not confined to one row/col
    assert len(actions) == 0


def test_pointing_pairs_no_action_when_no_outside_candidate():
    """
    Even if a candidate is confined to a single row (or column) inside the block,
    if there are no cells outside the block in that row/column that contain the
    candidate, then no eliminations should be produced.
    """
    field = Field("0" * 81)
    _set_all_cells_hopeful(field, {1, 2, 3})

    # Put candidate 4 in two cells inside block 4 that are both in row 4 (middle row of the block)
    # Choose block 4 (center block, idx=4) which covers x=3..5,y=3..5. Use row y=3 for the example.
    in_block_a = field.get_cell(3, 3)
    in_block_b = field.get_cell(4, 3)
    in_block_a.hopeful.add(4)
    in_block_b.hopeful.add(4)

    # Ensure no cell outside the block in that row contains 4
    outside_row_cells = [
        c for c in field.get_group("row", 3) if c not in field.get_group("block", 4)
    ]
    for c in outside_row_cells:
        # Guarantee 4 is not present outside the block in that row
        if 4 in c.hopeful:
            c.hopeful.remove(4)

    group = field.get_group("block", 4)
    actions = list(pointing_pairs(field, type="block", idx=4, group=group))

    assert len(actions) == 0


if __name__ == "__main__":
    pytest.main([__file__])
