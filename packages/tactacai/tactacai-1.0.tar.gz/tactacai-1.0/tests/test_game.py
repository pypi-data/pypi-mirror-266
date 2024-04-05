import unittest
from tactacai.game import Game
from tactacai.game import empty_cells, wins


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_wins(self):
        # Test wins function
        state = [['X', ' ', ' '], ['O', 'X', 'O'], [' ', ' ', 'X']]
        self.assertTrue(wins(state, 'X'))
        self.assertFalse(wins(state, 'O'))

    def test_empty_cells(self):
        # Test empty_cells function
        state = [['X', ' ', ' '], ['O', 'X', 'O'], [' ', ' ', 'X']]
        self.assertEqual(empty_cells(state), [[0, 1], [0, 2], [2, 0], [2, 1]])

    def test_evaluate(self):
        # Test evaluate function
        state1 = [['X', 'X', 'X'], [' ', 'O', 'O'], [' ', ' ', ' ']]
        state2 = [['O', 'O', 'O'], [' ', 'X', 'X'], [' ', ' ', ' ']]
        state3 = [['X', 'O', 'X'], [' ', 'O', 'X'], [' ', 'X', 'O']]
        self.assertEqual(self.game.evaluate(state1), -1)  # X wins
        self.assertEqual(self.game.evaluate(state2), 1)  # O winner
        self.assertEqual(self.game.evaluate(state3), 0)  # No winner

    def test_game_over(self):
        # Test game_over function
        state1 = [['X', 'X', 'X'], [' ', 'O', 'O'], [' ', ' ', ' ']]
        state2 = [['O', 'O', ' '], ['X', 'X', 'X'], [' ', ' ', ' ']]
        state3 = [['X', 'O', 'X'], [' ', 'O', 'X'], [' ', 'X', 'O']]
        self.assertTrue(self.game.game_over(state1))  # X wins
        self.assertTrue(self.game.game_over(state2))  # X wins
        self.assertFalse(self.game.game_over(state3))  # No winner


if __name__ == '__main__':
    unittest.main()
