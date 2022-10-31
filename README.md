# Sudoku - tools

A [sudoku] is logic puzzle, where each number is only allowed once per row, column and box. The purpose of this tools is, to provide a game, that can help you to get better over time.

## implemented features

* Solver
  * solved
  * show_possibles
  * singles
  * naked_pairs
  * naked_triples
  * hidden_pairs
  * hidden_tripples
  * pointing_pairs
  * box_line_reduction
  * xwing
  * single_chain (rule 4)
* GUI
  * showing the board
  * showing possible numbers
  * saving a board
  * loading a board


## Planned features
* Solver
  * single_chain (rule 2)
  * y_wing
  * sword_fish
  * xyz_wing (?)
* GUI
  * possibility to play a game
  * mouse / touch only use
  * keyboard only use
  * logical hints
    * instead of revealing a random number, they should provide tips how to move forward
    * the tips should start vague, like: `look for pointing pairs`
    * if you still don't get it, it should be more specific like: `look in rows`
    * then it could tell you the specific row
    * in the end could show you the specific pointing pair
  *


[sudoku]: https://en.wikipedia.org/wiki/Sudoku
The goal of this program is to have a collection of sudoku tools.

Planned is a solver, a tool to rate the difficulty of sudokus, a universal sudoku game, and a game mode that gives you useful hints when you get stuck. Or even lets you train to find specific reduction techniques.

## More information

Sudokuwiki has a great list of techniques on how to solve sudokus. These can be used to grade puzzles.

https://www.sudokuwiki.org/sudoku.htm

## Example of an hard sudoku

hard:63.....81.2...3.......1743..964..57....762....8....6...6..2....3.9....6.........9
