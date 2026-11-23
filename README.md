# Sudoku

A Sudoku solver, puzzle generator and terminal game written in plain Python 3.9+ (no dependencies).

## Features

- **Solver**: backtracking with the "most constrained cell first" heuristic.
- **Generator**: builds a random full grid, then removes cells while checking the puzzle still has exactly one solution.
- **Terminal game**: enter moves, ask for hints, or reveal the solution.
- **Tests**: unit tests with `unittest`.

## Usage

```bash
python sudoku.py play                 # play a new puzzle
python sudoku.py play --clues 30      # harder (fewer given digits)
python sudoku.py generate             # print a puzzle and its 81-char string
python sudoku.py solve 530070000600195000098000060800060003400803001700020006060000280000419005000080079
```

In the game: type `row col digit` (e.g. `3 4 7`), `clear row col`, `hint`, `solve` or `quit`.

## Run the tests

```bash
python -m unittest -v
```

## How it works

1. `candidates` finds which digits fit a cell (row, column and 3x3 box rules).
2. `solve` always picks the empty cell with the fewest options, tries each, and backtracks on dead ends.
3. `count_solutions` stops after finding 2 solutions, which is enough to know a puzzle is not unique.
4. `generate` removes cells one at a time and keeps a removal only if the puzzle stays unique.

## Ideas for next steps

- Difficulty ratings based on which solving techniques are needed
- A GUI (tkinter) or web version
- Human-style solving techniques (naked singles, pairs, X-wing)
- Benchmarks comparing solving strategies
