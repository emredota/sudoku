import unittest

import sudoku

PUZZLE = (
    "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
)


class SudokuTests(unittest.TestCase):
    def test_solves_known_puzzle(self):
        board = sudoku.parse(PUZZLE)
        self.assertTrue(sudoku.solve(board))
        self.assertTrue(sudoku.is_solved(board))

    def test_solution_keeps_givens(self):
        original = sudoku.parse(PUZZLE)
        board = sudoku.parse(PUZZLE)
        sudoku.solve(board)
        for r in range(9):
            for c in range(9):
                if original[r][c]:
                    self.assertEqual(original[r][c], board[r][c])

    def test_unsolvable_detected(self):
        board = sudoku.parse(PUZZLE)
        board[0][2] = 5  # duplicates the 5 already in row 0
        self.assertFalse(sudoku.solve(board))

    def test_generated_puzzle_is_unique_and_valid(self):
        puzzle, solution = sudoku.generate(clues=40)
        self.assertTrue(sudoku.is_solved(solution))
        self.assertEqual(sudoku.count_solutions(puzzle), 1)
        clues = sum(1 for row in puzzle for v in row if v)
        self.assertGreaterEqual(clues, 40)

    def test_parse_rejects_bad_length(self):
        with self.assertRaises(ValueError):
            sudoku.parse("123")

    def test_is_valid_placement(self):
        board = sudoku.parse(PUZZLE)
        self.assertFalse(sudoku.is_valid_placement(board, 0, 2, 5))
        self.assertTrue(sudoku.is_valid_placement(board, 0, 2, 4))


if __name__ == "__main__":
    unittest.main()
