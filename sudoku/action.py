from typing import Literal, NamedTuple, TypeAlias

from .cell import Cell

action_str: TypeAlias = Literal["remove_possible", "set_number"]


class Action(NamedTuple):
    """
    Action is a NamedTuple that contains suggested changes to a :class:`sudoku.field.Field`

    `action` is either "remove_possible" or "set_number"

    `value` is an interger from 1 to 9

    `cell` is the cell, where this action could be applied

    `reason` is a string that will be appended to the `_debug` list to cell if `action` is "remove_possible"

    """

    action: action_str
    value: int
    cell: Cell
    reason: str
