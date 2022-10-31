# Implemented Solvers

Here we describe short the rules that where followed to implemented the solvers.

## Solved

Whenever you have an empty cell, that can only have one possible value you can set it to this value.

## Singles

Whenever you have a group where a number is only possible in one cell. You can set this cell to the number.

## Show possibles

For each group, look at all cells that have a value and remove it as a possiblity from all cells that don't have a value.

## Naked Pairs

If you find two cells in a group, where the only possible numbers are the same two numbers, you can remove those numbers
from the possible numbers from any other cell in that group. Those numbers can only appear in either of those two cells,
which will remove them from the other cells.

## Naked Triples

It is very similar to the naked pairs, but works with a set of three numbers in three different cells. Those are a bit
harder to catch, since not all of them have to appear in each cell. It could even happen that the three cells have only
2 numbers each, like `1` `2`, `2` `3`, and `1` `3`.

## Hidden pairs

Is also similar to the naked single, but you need to find two numbers, that are only possible to pick for the same two
cells. In this case you know that these cells can only be set to either of the number and you can remove all other
possibilities for those two cells.

## Hidden triples

This the same to hidden pairs, as naked triples was to naked pairs.

## Pointing pairs

If in one block all possible positions for a specific number are only in one row or column, all other cells in other blocks
of this row or column can be this number.

## Box Line Reduction

If in one row, a specific number is only possible in one group, this group can only place this number in this specific row
or column.

## X-Wing

When you have 2 rows where a number is only possible at the same 2 columns, you know that the this numer cannot be present
in any other row at this colum. This also works when you change column with row.

## Simple Chain

To build a chain graph, add all 2 cell connections where only 2 cells have a specific number possible. After you added
all possible cells, start colouring them with 2 colors that neighbours don't have the same color. Now you can look at all other
cells where this number is possible that are not part of the chain and if they can see two or more cells from the chain
that have different colours, you know that this number is not possible on this cell.
Another way is to look at the chain it self, when you find two or more cells in the same group, you know that this color cannot be
set and solve the whole chain to set all cells of the chain with the other color.

## Single Chain Rule 2 (not implemented)

This rule is shared with 3D Medusa (at this moment there is no plan to implement the Medusa solver). Here you are looking for one nubmer at a time. You check all block that have the number only twice and color them in two different coulurs. When you build the whole graph but found multiple numbers with the same colour in the same block you eliminate all of them.
