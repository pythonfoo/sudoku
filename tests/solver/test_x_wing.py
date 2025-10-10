import pytest

from sudoku.field import Field
from sudoku.solver.x_wing import x_wing


def _set_all_cells_hopeful(field: Field, hopeful_set: set[int]) -> None:
    """Helper to set the hopeful set for every cell in a field."""
    for cell in field.cells:
        cell.hopeful = set(hopeful_set)


def test_x_wing_row_elimination_basic():
    """
    Basic X-Wing scenario (row-based detection):

    - We ensure the candidate `4` appears only in two columns (1 and 5) for two rows (2 and 6).
    - There are other cells in columns 1 and 5 (but different rows) that also contain 4.
    -> The solver should produce removal actions removing `4` from those other cells in the same columns.
    """
    field = Field("0" * 81)
    # baseline hopefuls that do NOT include the tested candidate (4)
    _set_all_cells_hopeful(field, {1, 2, 3})

    candidate = 4
    col_a, col_b = 1, 5
    row_a, row_b = 2, 6

    # X-Wing corners (these four should remain possible for candidate)
    a = field.get_cell(col_a, row_a)
    b = field.get_cell(col_b, row_a)
    c = field.get_cell(col_a, row_b)
    d = field.get_cell(col_b, row_b)
    for cell in (a, b, c, d):
        cell.hopeful.add(candidate)

    # Victim cells: in the same two columns, but different rows -> should be eliminated
    victim1 = field.get_cell(col_a, 0)
    victim2 = field.get_cell(col_a, 8)
    victim3 = field.get_cell(col_b, 4)
    for v in (victim1, victim2, victim3):
        v.hopeful.add(candidate)

    actions = list(x_wing(field))
    # collect removals mapped by cell
    removals = {}
    for act in actions:
        assert act.action == "remove_possible"
        assert act.value == candidate
        removals.setdefault(act.cell, set()).add(act.value)

    # Expect exactly the three victim cells to be targeted
    assert removals.get(victim1) == {candidate}
    assert removals.get(victim2) == {candidate}
    assert removals.get(victim3) == {candidate}

    # Ensure the four X-Wing corner cells were NOT targeted
    assert a not in removals
    assert b not in removals
    assert c not in removals
    assert d not in removals


def test_x_wing_column_elimination_basic():
    """
    Basic X-Wing scenario (column-based detection):

    - Candidate `5` appears only in two rows (0 and 5) for two columns (2 and 7).
    - There are other cells in rows 0 and 5 (but different columns) that also contain 5.
    -> The solver should produce removal actions removing `5` from those other cells in the same rows.
    """
    field = Field("0" * 81)
    _set_all_cells_hopeful(field, {1, 2, 3})

    candidate = 5
    col_a, col_b = 2, 7
    row_a, row_b = 0, 5

    # X-Wing corners (these four should remain possible for candidate)
    a = field.get_cell(col_a, row_a)
    b = field.get_cell(col_b, row_a)
    c = field.get_cell(col_a, row_b)
    d = field.get_cell(col_b, row_b)
    for cell in (a, b, c, d):
        cell.hopeful.add(candidate)

    # Victim cells: in the same two rows (row_a, row_b) but different columns -> should be eliminated
    victim1 = field.get_cell(0, row_a)
    victim2 = field.get_cell(4, row_a)
    victim3 = field.get_cell(8, row_b)
    for v in (victim1, victim2, victim3):
        v.hopeful.add(candidate)

    actions = list(x_wing(field))
    removals = {}
    for act in actions:
        assert act.action == "remove_possible"
        assert act.value == candidate
        removals.setdefault(act.cell, set()).add(act.value)

    assert removals.get(victim1) == {candidate}
    assert removals.get(victim2) == {candidate}
    assert removals.get(victim3) == {candidate}

    # corners must not be removed
    assert a not in removals
    assert b not in removals
    assert c not in removals
    assert d not in removals


def test_x_wing_no_false_positive_when_positions_mismatch():
    """
    Ensure no false positives:
    - Two rows have the candidate, but in different sets of columns (not identical pairs).
    -> No X-Wing should be detected and no removals should be produced.
    """
    field = Field("0" * 81)
    _set_all_cells_hopeful(field, {1, 2, 3})

    candidate = 6
    # Row 1 has candidate in cols 1 and 2
    r1_cells = [field.get_cell(1, 1), field.get_cell(2, 1)]
    # Row 3 has candidate in cols 1 and 3 (different pair -> no x-wing)
    r3_cells = [field.get_cell(1, 3), field.get_cell(3, 3)]

    for c in r1_cells + r3_cells:
        c.hopeful.add(candidate)

    # A victim in col 1 elsewhere that should NOT be removed because there is no X-Wing
    victim = field.get_cell(1, 5)
    victim.hopeful.add(candidate)

    actions = list(x_wing(field))
    # No removal actions should be present for candidate
    for act in actions:
        assert not (
            act.action == "remove_possible" and act.value == candidate
        ), "Unexpected removal for candidate in non-X-Wing pattern"

    # Sanity: ensure victim still has the candidate available
    assert candidate in victim.hopeful


if __name__ == "__main__":
    pytest.main([__file__])
