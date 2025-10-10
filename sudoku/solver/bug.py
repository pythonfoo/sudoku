"""
Implementation of https://www.sudokuwiki.org/BUG

It is an endgame technique, it can be solved also by xy chain which is a bit more general and complicated.
"""

from collections import Counter

from sudoku.action import Action
from sudoku.cell import Cell
from sudoku.field import Field

from .utils import Generator


def bug(field: Field) -> Generator[Action]:
    group_types = ["row", "column", "block"]
    bug: Cell | None = None
    for cell in field.cells:
        match len(cell.hopeful):
            case 0:
                continue
            case 1:
                # This cell is already solved, ignore it
                return
            case 2:
                print(f"{cell!r}")

                continue
            case 3:
                print(f"{cell!r}")

                if bug is not None:
                    # More than one cell with 3 candidates, can't be BUG
                    return
                bug = cell
            case _:
                print(f"ERORR: {cell!r}")

                # More than 3 candidates in a cell, can't be BUG
                return

    if bug is None:
        # No cell with exactly 3 candidates, can't be BUG
        return

    # verify it is a BUG, for each group type we need each candidate to appear exactly twice,
    # only one of them will appear 3 times

    bug_value: int | None = None
    for group_type in group_types:
        group_idx = getattr(bug.position, group_type)
        group = field.get_group(group_type, group_idx)
        hopeful_counter = Counter()
        for cell in group:
            if not cell.hopeful:
                continue
            hopeful_counter.update(cell.hopeful)
        match hopeful_counter.most_common(2):
            case [(value1, 3), (_, 2)]:
                if bug_value is None:
                    bug_value = value1
                elif bug_value != value1:
                    # The value that appears 3 times must be the same in all groups
                    return
            case _:
                # The counts don't match the BUG pattern
                # It only tolerates one value appearing 3 times, all others must appear exactly twice
                return

    if bug_value is None:
        # This should not happen, but just in case
        return

    yield Action(
        action="set_value",
        value=bug_value,
        cell=bug,
        reason=f"BUG found, setting cell at {bug.position} to {bug_value}",
    )
