import pytest

from sudoku.action import Action
from sudoku.field import Field
from sudoku.solver.bug import bug
from sudoku.solver.show_possibles import show_possibles
from sudoku.types import CellPosition


@pytest.mark.parametrize(
    "puzzle_str, expected_action_values",
    [
        pytest.param(
            "174832596593461278682957001067500900019703605435096807301600759908075060756309082",
            (
                "set_value",
                2,
                "D8",
            ),
        )
    ],
)
def test_bug(puzzle_str, expected_action_values):
    field = Field(puzzle_str)
    for action in show_possibles(field):
        field.apply(action)
    print(field)

    field.get_cell("D5").hopeful = {1, 2}
    field.get_cell("D8").hopeful = {1, 2, 3}
    field.get_cell("E5").hopeful = {4, 8}
    field.get_cell("G5").hopeful = {2, 8}
    field.get_cell("H7").hopeful = {1, 3}

    # only one cell (D8) with 3 hopefuls
    for cell in field.cells:
        if len(cell.hopeful) > 2:
            print(f"Cell {cell.position}: value={cell.value}, hopeful={cell.hopeful}")

    actions = list(bug(field))

    assert len(actions) == 1, f"Expected 1 action, got {len(actions)}"
    action = actions[0]
    action_values = (action.action, action.value, action.cell.position.as_sudokuwiki())
    assert (
        action_values == expected_action_values
    ), f"Expected action values {expected_action_values}, got {action_values}"
