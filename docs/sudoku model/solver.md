# Solvers

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

Todo

## Simple Chain

Todo

