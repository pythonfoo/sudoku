```{toctree}
:hidden:

cell_source
field_source
types
solver
```

# The Sudoku Model

A sudoku game consists of a {ref}`Field <field>` with 81 {ref}`Cells <cell>`. 9 cells per row, and 9 cells per column. It has also 9 {ref}`groups or blocks <block>` that have 3 rows and columns each.

(field)=
## The Field

{class}`sudoku.field.Field`

(block)=
## The Block

The block is a region of 9 {ref}`cells <cell>` spawning multiple columns and rows. Typical sudokus creating them by dividing the 9 by 9 field into 9 smaller 3 x 3 squares. There are also sudoku variants that choose different layouts for the blocks, like jigsaw sudokus or Aztec sudokus.

```{important}
Never assume to which `block` a `cell` belongs based on the `column` and `row`, but always check the `block` property of the {class}`sudoku.cell.Cell.position`.

When you need to get all members of a specific block, you can use the {class}`sudoku.field.Field.get_group` method and pass `"block"` as the `type` argument.
```

```{todo}
add images of different sudoku variants
```

(cell)=
## The Cell

{class}`sudoku.cell.Cell`
