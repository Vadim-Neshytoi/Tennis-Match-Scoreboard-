import unittest
from unittest.mock import MagicMock
from application.dto.finished_matches_result import FinishedMatchesResult
from mappers.finished_match_view_mapper import FinishedMatchViewMapper


class TestFinishedMatchViewMapper(unittest.TestCase):

    def test_finished_match_view_mapper(self) -> None:
        self.finished_match_view_mapper = FinishedMatchViewMapper()
        finished_match_result = FinishedMatchesResult(matches=[MagicMock() for _ in range(30)], total_count=30, items_per_page=10,
                                                      total_pages=3, current_page=2, player_name="Alex Smith")

        result = self.finished_match_view_mapper.to_view_data(finished_match_result)

        self.assertEqual(len(result["matches"]), 30)
        self.assertEqual(result["total_count"], 30)
        self.assertEqual(result["items_per_page"], 10)
        self.assertEqual(result["total_pages"], 3)
        self.assertEqual(result["current_page"], 2)
        self.assertEqual(result["pagination"]["previous_url"], "/matches?page=1&filter_by_player_name=Alex+Smith")
        self.assertEqual(result["pagination"]["pages"][0], {'number': 1, 'url': '/matches?page=1&filter_by_player_name=Alex+Smith'})
        self.assertEqual(result["pagination"]["pages"][1], {'number': 2, 'url': '/matches?page=2&filter_by_player_name=Alex+Smith'})
        self.assertEqual(result["pagination"]["pages"][2], {'number': 3, 'url': '/matches?page=3&filter_by_player_name=Alex+Smith'})
        self.assertEqual(result["pagination"]["next_url"], "/matches?page=3&filter_by_player_name=Alex+Smith")




















