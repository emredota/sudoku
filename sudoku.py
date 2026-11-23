"""Sudoku: solver, puzzle generator, and a small terminal game.

Usage:
    python sudoku.py play [--clues 36]
    python sudoku.py solve <81-char puzzle string, 0 or . for empty>
    python sudoku.py generate [--clues 36]
"""
from __future__ import annotations

import argparse
import random
import sys
from copy import deepcopy

Board = list[list[int]]
SIZE = 9
BOX = 3


# --------------------------------------------------------------------------
# Core logic
# --------------------------------------------------------------------------
def empty_board() -> Board:
    return [[0] * SIZE for _ in range(SIZE)]


def candidates(board: Board, r: int, c: int) -> list[int]:
    """Digits that can legally go into (r, c) given the current board."""
    used = set(board[r]) | {board[i][c] for i in range(SIZE)}
    br, bc = r // BOX * BOX, c // BOX * BOX
    used |= {board[i][j] for i in range(br, br + BOX) for j in range(bc, bc + BOX)}
    return [v for v in range(1, 10) if v not in used]


def is_valid_placement(board: Board, r: int, c: int, v: int) -> bool:
    return board[r][c] == 0 and v in candidates(board, r, c)


def _best_empty(board: Board):
    """Pick the empty cell with the fewest candidates (MRV heuristic)."""
    best = None
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                cands = candidates(board, r, c)
                if best is None or len(cands) < len(best[2]):
                    best = (r, c, cands)
                    if len(cands) <= 1:
                        return best
    return best


def solve(board: Board, randomize: bool = False) -> bool:
    """Solve in place with backtracking. Returns True if solved."""
    cell = _best_empty(board)
    if cell is None:
        return True
    r, c, cands = cell
    if randomize:
        random.shuffle(cands)
    for v in cands:
        board[r][c] = v
        if solve(board, randomize):
            return True
    board[r][c] = 0
    return False


def count_solutions(board: Board, limit: int = 2) -> int:
    """Count solutions, stopping early at `limit` (2 is enough to test uniqueness)."""
    b = deepcopy(board)

    def rec() -> int:
        cell = _best_empty(b)
        if cell is None:
            return 1
        r, c, cands = cell
        total = 0
        for v in cands:
            b[r][c] = v
            total += rec()
            if total >= limit:
                break
        b[r][c] = 0
        return total

    return rec()


def generate(clues: int = 36) -> tuple[Board, Board]:
    """Return (puzzle, solution). The puzzle has a unique solution."""
    solution = empty_board()
    solve(solution, randomize=True)
    puzzle = deepcopy(solution)
    cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(cells)
    remaining = SIZE * SIZE
    for r, c in cells:
        if remaining <= clues:
            break
        saved = puzzle[r][c]
        puzzle[r][c] = 0
        if count_solutions(puzzle) != 1:
            puzzle[r][c] = saved
        else:
            remaining -= 1
    return puzzle, solution


def is_solved(board: Board) -> bool:
    full = set(range(1, 10))
    rows = all(set(row) == full for row in board)
    cols = all({board[r][c] for r in range(SIZE)} == full for c in range(SIZE))
    boxes = all(
        {board[br + i][bc + j] for i in range(BOX) for j in range(BOX)} == full
        for br in range(0, SIZE, BOX)
        for bc in range(0, SIZE, BOX)
    )
    return rows and cols and boxes


# --------------------------------------------------------------------------
# Parsing and display
# --------------------------------------------------------------------------
def parse(text: str) -> Board:
    chars = [ch for ch in text.strip() if not ch.isspace()]
    if len(chars) != 81:
        raise ValueError(f"Expected 81 cells, got {len(chars)}")
    digits = [0 if ch in "0." else int(ch) for ch in chars]
    return [digits[i * 9:(i + 1) * 9] for i in range(9)]


def render(board: Board, given: Board | None = None) -> str:
    lines = ["    1 2 3   4 5 6   7 8 9", "  +-------+-------+-------+"]
    for r in range(SIZE):
        parts = []
        for c in range(SIZE):
            v = board[r][c]
            parts.append("." if v == 0 else str(v))
        row = " | ".join(
            " ".join(parts[i:i + 3]) for i in range(0, 9, 3)
        )
        lines.append(f"{r + 1} | {row} |")
        if r % 3 == 2:
            lines.append("  +-------+-------+-------+")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Terminal game
# --------------------------------------------------------------------------
HELP = "Commands: 'row col digit' (e.g. 3 4 7), 'clear row col', 'hint', 'solve', 'quit'"


def play(clues: int) -> None:
    print("Generating puzzle...")
    puzzle, solution = generate(clues)
    board = deepcopy(puzzle)
    print(HELP)
    while True:
        print(render(board))
        if is_solved(board):
            print("Solved! Nice work.")
            return
        try:
            line = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        parts = line.split()
        if not parts:
            continue
        if parts[0] in ("q", "quit"):
            return
        if parts[0] == "solve":
            print(render(solution))
            return
        if parts[0] == "hint":
            empties = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] == 0]
            r, c = random.choice(empties)
            board[r][c] = solution[r][c]
            print(f"Hint: row {r + 1}, col {c + 1} = {solution[r][c]}")
            continue
        try:
            if parts[0] == "clear":
                r, c = int(parts[1]) - 1, int(parts[2]) - 1
                if puzzle[r][c] != 0:
                    print("That cell is part of the puzzle.")
                else:
                    board[r][c] = 0
                continue
            r, c, v = int(parts[0]) - 1, int(parts[1]) - 1, int(parts[2])
            if not (0 <= r < 9 and 0 <= c < 9 and 1 <= v <= 9):
                raise ValueError
        except (ValueError, IndexError):
            print(HELP)
            continue
        if puzzle[r][c] != 0:
            print("That cell is part of the puzzle.")
            continue
        board[r][c] = 0
        if v in candidates(board, r, c):
            board[r][c] = v
        else:
            print("That breaks a Sudoku rule (row, column or box).")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Sudoku solver, generator and game")
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("play", help="play in the terminal")
    sp.add_argument("--clues", type=int, default=36)
    sg = sub.add_parser("generate", help="print a new puzzle")
    sg.add_argument("--clues", type=int, default=36)
    ss = sub.add_parser("solve", help="solve a puzzle string")
    ss.add_argument("puzzle")
    args = p.parse_args(argv)

    if args.cmd == "play":
        play(args.clues)
    elif args.cmd == "generate":
        puzzle, _ = generate(args.clues)
        print(render(puzzle))
        print("String:", "".join(str(v) for row in puzzle for v in row))
    else:
        board = parse(args.puzzle)
        if solve(board):
            print(render(board))
        else:
            print("No solution.")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
