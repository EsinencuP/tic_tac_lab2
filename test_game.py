"""Проверки правил и всех ответов человека на стратегию ИИ."""

import unittest
from unittest.mock import patch

from main import (
    DRAW, GameState, apply_move, choose_best_move, evaluate,
    get_legal_moves, minimax, play, read_human_move, terminal_result,
)


class GameTests(unittest.TestCase):
    def test_terminal_states(self):
        for board, result, score in (
            ("OOOXX    ", "O", 10),
            ("XXXOO    ", "X", -10),
            ("XOXXOOOXX", DRAW, 0),
        ):
            state = GameState(tuple(board))
            self.assertEqual(terminal_result(state), result)
            self.assertEqual(evaluate(state), score)
            self.assertEqual(get_legal_moves(state), [])
        self.assertIsNone(terminal_result(GameState()))

    def test_all_winning_lines(self):
        lines = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
                 (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
        for symbol in ("X", "O"):
            for line in lines:
                board = [" "] * 9
                for index in line:
                    board[index] = symbol
                self.assertEqual(terminal_result(GameState(tuple(board))), symbol)

    def test_move_is_immutable_and_validated(self):
        initial = GameState()
        child = apply_move(initial, 4)
        self.assertEqual(initial.board[4], " ")
        self.assertEqual(child.board[4], "X")
        self.assertEqual(child.current_player, "O")
        for move in (4, -1, 9):
            with self.assertRaises(ValueError):
                apply_move(child, move)

    def test_report_example(self):
        state = GameState(tuple("XX  O    "), "O", "O")
        scores = {move + 1: minimax(apply_move(state, move), 1, False)
                  for move in get_legal_moves(state)}
        self.assertEqual(scores, {3: 0, 4: -10, 6: -10, 7: -10, 8: -10, 9: -10})
        self.assertEqual(choose_best_move(state), 2)

    def test_ai_never_loses(self):
        # Все ходы человека, на ходу ИИ — реальный choose_best_move.
        # Обход без кэша: проверяются все истории против этой стратегии.
        def visit(state):
            result = terminal_result(state)
            if result is not None:
                self.assertIn(result, (state.ai, DRAW))
                return 1
            moves = ([choose_best_move(state)] if state.current_player == state.ai
                     else get_legal_moves(state))
            return sum(visit(apply_move(state, move)) for move in moves)

        for ai in ("X", "O"):
            count = visit(GameState(ai=ai))
            print(f"\nИИ = {ai}: проверено завершённых партий — {count}; поражений — 0")

    def test_console_input(self):
        state = apply_move(GameState(), 0)
        with patch("builtins.input", side_effect=["abc", "0", "10", "1", "5"]):
            self.assertEqual(read_human_move(state), 4)
        with patch("builtins.input", return_value="q"):
            with self.assertRaises(EOFError):
                read_human_move(state)

    def test_console_complete_game(self):
        # При равных оценках ИИ берёт первую клетку по номеру.
        with patch("builtins.input", side_effect=["X", "1", "2", "4"]):
            play()


if __name__ == "__main__":
    unittest.main()
