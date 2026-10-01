import unittest
from unittest.mock import MagicMock, patch
from models.player import Player
from models.match import Match
from mappers.match_view_mapper import MatchViewMapper


class TestMatchViewMapper(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_score_service = MagicMock()
        self.mock_score_service.is_tie_break.return_value = False
        self.mapper = MatchViewMapper(score_service=self.mock_score_service)


    def test_match_view_mapper_usual_points(self) -> None:
        player1 = Player("Alex", 1)
        player2 = Player("Bob", 2)
        domain_match = Match(player1, player2)
        cases = [
            (0, "0"),
            (1, "15"),
            (2, "30"),
            (3, "40"),
        ]

        for player_pts, expected_pts in cases:
            with self.subTest(f"Проверка преобразования очков {player_pts} в гейме в {expected_pts}"):
                domain_match.player_1_score.points = player_pts
                domain_match.player_2_score.points = player_pts
                result = self.mapper.to_view_data(domain_match)

                self.assertEqual(result["player1"]["points"], expected_pts)
                self.assertEqual(result["player2"]["points"], expected_pts)

    def test_match_view_mapper_deuce(self) -> None:
        player1 = Player("Alex", 1)
        player2 = Player("Bob", 2)
        domain_match = Match(player1, player2)
        cases = [
            (3, 3),
            (4, 4),
            (7, 7),
            (10, 10)
        ]

        for player_1_pts, player_2_pts in cases:
            with self.subTest(f"Проверка преобразования очков {player_1_pts}:{player_2_pts} в гейме"):
                domain_match.player_1_score.points = player_1_pts
                domain_match.player_2_score.points = player_2_pts
                result = self.mapper.to_view_data(domain_match)

                self.assertEqual(result["player1"]["points"], "40")
                self.assertEqual(result["player2"]["points"], "40")

    def test_match_view_mapper_advantage(self) -> None:
        player1 = Player("Alex", 1)
        player2 = Player("Bob", 2)
        domain_match = Match(player1, player2)
        cases = [
            (4, 3),
            (5, 4),
            (8, 7),
            (3, 4),
            (4, 5),
            (7, 8)
        ]

        for player_1_pts, player_2_pts in cases:
            with self.subTest(f"Проверка преобразования очков {player_1_pts}:{player_2_pts} в гейме"):
                domain_match.player_1_score.points = player_1_pts
                domain_match.player_2_score.points = player_2_pts
                result = self.mapper.to_view_data(domain_match)

                if player_1_pts > player_2_pts:
                    self.assertEqual(result["player1"]["points"], "AD")
                    self.assertEqual(result["player2"]["points"], "40")
                else:
                    self.assertEqual(result["player1"]["points"], "40")
                    self.assertEqual(result["player2"]["points"], "AD")

    def test_match_view_mapper_is_tie_break(self) -> None:
        player1 = Player("Alex", 1)
        player2 = Player("Bob", 2)
        domain_match = Match(player1, player2, winner=None)
        self.mock_score_service.is_tie_break.return_value = True
        cases = [
            (4, 3),
            (5, 4),
            (8, 7),
            (10, 8)
        ]

        for player_1_pts, player_2_pts in cases:
            with self.subTest(f"Проверка преобразования очков {player_1_pts}:{player_2_pts} при тай брейке"):
                domain_match.player_1_score.points = player_1_pts
                domain_match.player_2_score.points = player_2_pts
                domain_match.player_1_score.games = 6
                domain_match.player_2_score.games = 6
                domain_match.player_1_score.sets = 1
                domain_match.player_2_score.sets = 0
                with patch.object(self.mapper, "get_display_points") as mock_display_points:
                    result = self.mapper.to_view_data(domain_match)
                    mock_display_points.assert_not_called()
                    expected_result = {
                        "uuid": domain_match.uuid,
                        "player1": {"name": "Alex",
                                    "id": player1.id,
                                    "points": player_1_pts,
                                    "games": 6,
                                    "sets": 1},
                        "player2": {"name": "Bob",
                                    "id": player2.id,
                                    "points": player_2_pts,
                                    "games": 6,
                                    "sets": 0},
                        "winner": None
                    }

                self.assertEqual(result, expected_result)
                self.mock_score_service.is_tie_break.assert_called_once()
                self.mock_score_service.is_tie_break.reset_mock()

    def test_match_view_mapper_transforms_match_to_view_data(self) -> None:
        player1 = Player("Alex", 1)
        player2 = Player("Bob", 2)
        domain_match = Match(player1, player2, winner=player1)
        domain_match.player_1_score.points = 0
        domain_match.player_1_score.games = 0
        domain_match.player_1_score.sets = 2
        domain_match.player_2_score.points = 0
        domain_match.player_2_score.games = 0
        domain_match.player_2_score.sets = 1

        expected_result =  {
            "uuid": domain_match.uuid,
            "player1": {"name": "Alex",
                        "id": player1.id,
                        "points": "0",
                        "games": 0,
                        "sets": 2},
            "player2": {"name": "Bob",
                        "id": player2.id,
                        "points": "0",
                        "games": 0,
                        "sets": 1},
            "winner": player1.name
        }

        result = self.mapper.to_view_data(domain_match)

        self.assertEqual(result, expected_result)































