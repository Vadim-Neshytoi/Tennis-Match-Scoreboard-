import unittest
from exceptions.validation_exceptions import PlayerNotInMatchError
from models.match import Match
from models.player import Player
from services.match_score_service import MatchScoreService


class TestMatchScoreService(unittest.TestCase):


    def setUp(self) -> None:
        self.player_1 = Player(name="Kalvin", ID=1)
        self.player_2 = Player(name="David", ID=2)
        self.match = Match(player_1=self.player_1, player_2=self.player_2)
        self.match_score_service = MatchScoreService()

    def set_points(self, player_1_points: int, player_2_points: int) -> None:
        self.match.player_1_score.points = player_1_points
        self.match.player_2_score.points = player_2_points

    def set_games(self, player_1_games: int, player_2_games: int) -> None:
        self.match.player_1_score.games = player_1_games
        self.match.player_2_score.games = player_2_games

    def set_sets(self, player_1_sets: int, player_2_sets: int) -> None:
        self.match.player_1_score.sets = player_1_sets
        self.match.player_2_score.sets = player_2_sets

    def assert_points(self, expected_player_1_points: int, expected_player_2_points: int) -> None:
        self.assertEqual(self.match.player_1_score.points, expected_player_1_points)
        self.assertEqual(self.match.player_2_score.points, expected_player_2_points)

    def assert_games(self, expected_player_1_games: int, expected_player_2_games: int) -> None:
        self.assertEqual(self.match.player_1_score.games, expected_player_1_games)
        self.assertEqual(self.match.player_2_score.games, expected_player_2_games)

    def assert_sets(self, expected_player_1_sets: int, expected_player_2_sets: int) -> None:
        self.assertEqual(self.match.player_1_score.sets, expected_player_1_sets)
        self.assertEqual(self.match.player_2_score.sets, expected_player_2_sets)

    def assert_winner(self, actual_winner: None | int, expected_winner: None | int) -> None:
        self.assertEqual(actual_winner, expected_winner)


    def test_award_points_player_1(self) -> None:
        self.match_score_service.award_point(self.match, self.player_1)

        self.assertEqual(self.match.player_1_score.points, 1)
        self.assertEqual(self.match.player_2_score.points, 0)

    def test_award_points_player_2(self) -> None:
        self.match_score_service.award_point(self.match, self.player_2)

        self.assertEqual(self.match.player_1_score.points, 0)
        self.assertEqual(self.match.player_2_score.points, 1)

    def test_exception_player_not_in_match(self) -> None:
        player_3 = Player("Player 3", 3)

        with self.assertRaises(PlayerNotInMatchError):
            self.match_score_service.award_point(self.match, player_3)

    def test_award_game_player_1(self) -> None:
        self.match_score_service.award_game(self.match, self.player_1)

        self.assertEqual(self.match.player_1_score.games, 1)
        self.assertEqual(self.match.player_2_score.games, 0)

    def test_award_game_player_2(self) -> None:
        self.match_score_service.award_game(self.match, self.player_2)

        self.assertEqual(self.match.player_1_score.games, 0)
        self.assertEqual(self.match.player_2_score.games, 1)

    def test_award_set_player_1(self) -> None:
        self.match_score_service.award_set(self.match, self.player_1)

        self.assertEqual(self.match.player_1_score.sets, 1)
        self.assertEqual(self.match.player_2_score.sets, 0)

    def test_award_set_player_2(self) -> None:
        self.match_score_service.award_set(self.match, self.player_2)

        self.assertEqual(self.match.player_1_score.sets, 0)
        self.assertEqual(self.match.player_2_score.sets, 1)

    def test_reset_points(self) -> None:
        self.set_points(player_1_points=4, player_2_points=1)

        self.match_score_service.reset_points(self.match)

        self.assertEqual(self.match.player_1_score.points, 0)
        self.assertEqual(self.match.player_2_score.points, 0)

    def test_reset_games(self) -> None:
        self.set_games(player_1_games=6, player_2_games=3)

        self.match_score_service.reset_games(self.match)

        self.assertEqual(self.match.player_1_score.games, 0)
        self.assertEqual(self.match.player_2_score.games, 0)

    def test_is_tie_break_true(self) -> None:
        self.set_games(player_1_games=6, player_2_games=6)

        result = self.match_score_service.is_tie_break(self.match)

        self.assertTrue(result)

    def test_is_tie_break_false(self) -> None:
        self.set_games(player_1_games=5, player_2_games=5)

        result = self.match_score_service.is_tie_break(self.match)

        self.assertFalse(result)

    def test_check_game_winner(self) -> None:
        cases = [
            (4, 3, None),
            (3, 3, None),
            (4, 2, self.player_1),
            (8, 6, self.player_1),
        ]
        for player_1_pts, player_2_pts, expected_winner in cases:
            with self.subTest(f"Проверка для счета {player_1_pts}:{player_2_pts} очков в гейме"):
                self.set_points(player_1_pts, player_2_pts)
                actual_winner = self.match_score_service.check_game_winner(self.match)

                if expected_winner is None:
                    self.assertIsNone(actual_winner)
                else:
                    self.assertIsNotNone(actual_winner)
                    self.assertEqual(actual_winner.id, expected_winner.id)

    def test_check_tie_break_winner(self) -> None:
        cases = [
            (7, 6, None),
            (7, 0, self.player_1),
            (7, 5, self.player_1),
            (6, 8, self.player_2)
        ]
        for player_1_pts, player_2_pts, expected_winner in cases:
            with self.subTest(f"Проверка для счета {player_1_pts}:{player_2_pts} очков в тай брейке"):
                self.set_points(player_1_pts, player_2_pts)
                actual_winner = self.match_score_service.check_tie_break_winner(self.match)

                if expected_winner is None:
                    self.assertIsNone(actual_winner)
                else:
                    self.assertIsNotNone(actual_winner)
                    self.assertEqual(actual_winner.id, expected_winner.id)


    def test_check_set_winner(self) -> None:
        cases = [
            (6, 5, None),
            (6, 6, None),
            (6, 0, self.player_1),
            (6, 4, self.player_1),
            (5, 7, self.player_2),
            (6, 7, self.player_2),
        ]
        for player_1_pts, player_2_pts, expected_winner in cases:
            with self.subTest(f"Проверка для счета {player_1_pts}:{player_2_pts} геймов в сете"):
                self.set_games(player_1_pts, player_2_pts)
                actual_winner = self.match_score_service.check_set_winner(self.match)

                if expected_winner is None:
                    self.assertIsNone(actual_winner)
                else:
                    self.assertIsNotNone(actual_winner)
                    self.assertEqual(actual_winner.id, expected_winner.id)


    def test_check_match_winner(self) -> None:
        cases = [
            (0, 0, None),
            (1, 1, None),
            (1, 0, None),
            (0, 1, None),
            (2, 0, self.player_1),
            (1, 2, self.player_2),
        ]
        for player_1_pts, player_2_pts, expected_winner in cases:
            with self.subTest(f"Проверка для счета {player_1_pts}:{player_2_pts} сетов в матче"):
                self.set_sets(player_1_pts, player_2_pts)
                actual_winner = self.match_score_service.check_match_winner(self.match)

                if expected_winner is None:
                    self.assertIsNone(actual_winner)
                else:
                    self.assertIsNotNone(actual_winner)
                    self.assertEqual(actual_winner.id, expected_winner.id)

    def test_play_match_award_points(self) -> None:
        actual_winner = self.match_score_service.play_match(match=self.match, player=self.player_1)

        self.assert_points(1, 0)
        self.assert_games(0, 0)
        self.assert_sets(0, 0)
        self.assert_winner(actual_winner, None)

    def test_play_match_end_games(self) -> None:
        self.set_points(player_1_points=3, player_2_points=2)

        actual_winner = self.match_score_service.play_match(match=self.match, player=self.player_1)

        self.assert_points(0, 0)
        self.assert_games(1, 0)
        self.assert_sets(0, 0)
        self.assert_winner(actual_winner, None)

    def test_play_match_end_sets(self) -> None:
        self.set_points(player_1_points=3, player_2_points=2)
        self.set_games(player_1_games=5, player_2_games=0)

        actual_winner = self.match_score_service.play_match(match=self.match, player=self.player_1)

        self.assert_points(0, 0)
        self.assert_games(0, 0)
        self.assert_sets(1, 0)
        self.assert_winner(actual_winner, None)

    def test_play_match_end_tie_break(self) -> None:
        self.set_points(player_1_points=6, player_2_points=0)
        self.set_games(player_1_games=6, player_2_games=6)

        actual_winner = self.match_score_service.play_match(match=self.match, player=self.player_1)

        self.assert_points(0, 0)
        self.assert_games(0, 0)
        self.assert_sets(1, 0)
        self.assert_winner(actual_winner, None)

    def test_play_match_end_match(self) -> None:
        self.set_points(player_1_points=3, player_2_points=2)
        self.set_games(player_1_games=5, player_2_games=0)
        self.set_sets(player_1_sets=1, player_2_sets=0)

        actual_winner = self.match_score_service.play_match(match=self.match, player=self.player_1)

        self.assert_points(0, 0)
        self.assert_games(0, 0)
        self.assert_sets(2, 0)
        self.assert_winner(actual_winner.id, self.player_1.id)

    def test_play_match_check_after_finished_match(self) -> None:
        self.set_points(player_1_points=0, player_2_points=0)
        self.set_games(player_1_games=0, player_2_games=0)
        self.set_sets(player_1_sets=2, player_2_sets=1)

        actual_winner = self.match_score_service.play_match(match=self.match, player=self.player_1)

        self.assert_points(0, 0)
        self.assert_games(0, 0)
        self.assert_sets(2, 1)
        self.assert_winner(actual_winner.id, self.player_1.id)

    def test_play_match_continue_game(self) -> None:
        self.set_points(player_1_points=3, player_2_points=3)
        self.set_games(player_1_games=5, player_2_games=0)

        actual_winner = self.match_score_service.play_match(match=self.match, player=self.player_1)

        self.assert_points(4, 3)
        self.assert_games(5, 0)
        self.assert_sets(0, 0)
        self.assert_winner(actual_winner, None)

    def test_play_match_continue_tie_break(self) -> None:
        self.set_points(player_1_points=6, player_2_points=6)
        self.set_games(player_1_games=6, player_2_games=6)

        actual_winner = self.match_score_service.play_match(match=self.match, player=self.player_1)

        self.assert_points(7, 6)
        self.assert_games(6, 6)
        self.assert_sets(0, 0)
        self.assert_winner(actual_winner, None)

    def test_play_match_exception_player_not_in_match(self) -> None:
        self.player_3 = Player(name="Alex", ID=3)

        with self.assertRaises(PlayerNotInMatchError):
            self.match_score_service.play_match(match=self.match, player=self.player_3)




if __name__ == '__main__':
    unittest.main()


















