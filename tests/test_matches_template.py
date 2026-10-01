import unittest
from unittest.mock import MagicMock
from pathlib import Path
from bs4 import BeautifulSoup # noqa
from presentation.template_renderer import TemplateRenderer
from application.dto.finished_matches_result import FinishedMatchesResult


class TestMatchesTemplate(unittest.TestCase):

    def setUp(self) -> None:
        current_dir = Path(__file__).resolve().parent
        templates_path = current_dir.parent / 'templates'
        self.renderer = TemplateRenderer(templates_path)
        self.template_name = "matches.html"

    def test_matches_pagination_preserves_filter(self) -> None:
        context = {
            "matches": [
                {"player1": "Alex Smith", "player2": "Bob", "winner": "Alex Smith"}
                for _ in range(10)
            ],
            "total_count": 30,
            "items_per_page": 10,
            "current_page": 2,
            "total_pages": 3,
            "pagination": {
                "previous_url": "/matches?page=1&filter_by_player_name=Alex+Smith",
                "pages": [
                    {"number": 1, "url": "/matches?page=1&filter_by_player_name=Alex+Smith"},
                    {"number": 2, "url": "/matches?page=2&filter_by_player_name=Alex+Smith"},
                    {"number": 3, "url": "/matches?page=3&filter_by_player_name=Alex+Smith"}
                ],
                "next_url": "/matches?page=3&filter_by_player_name=Alex+Smith"
            }
        }
        html_content = self.renderer.render(self.template_name, context)
        soup = BeautifulSoup(html_content, "html.parser")
        pagination = soup.find("div", class_="pagination")
        self.assertIsNotNone(pagination)
        previous_link = pagination.find("a", class_="prev")
        self.assertIsNotNone(previous_link)
        self.assertEqual(previous_link.get("href"),"/matches?page=1&filter_by_player_name=Alex+Smith")
        page_links = pagination.find_all("a", class_="num-page")
        self.assertEqual(len(page_links), 3)
        self.assertEqual(page_links[0].get("href"),"/matches?page=1&filter_by_player_name=Alex+Smith")
        self.assertEqual(page_links[1].get("href"),"/matches?page=2&filter_by_player_name=Alex+Smith")
        self.assertEqual(page_links[2].get("href"),"/matches?page=3&filter_by_player_name=Alex+Smith")
        next_link = pagination.find("a", class_="next")
        self.assertIsNotNone(next_link)
        self.assertEqual(next_link.get("href"),"/matches?page=3&filter_by_player_name=Alex+Smith")

    def test_matches_pagination_without_filter(self) -> None:
        context = {
            "matches": [
                {"player1": "Alex", "player2": "Bob", "winner": "Alex"}
                for _ in range(10)
            ],
            "total_count": 30,
            "items_per_page": 10,
            "current_page": 2,
            "total_pages": 3,
            "pagination": {
                "previous_url": "/matches?page=1",
                "pages": [
                    {"number": 1, "url": "/matches?page=1"},
                    {"number": 2, "url": "/matches?page=2"},
                    {"number": 3, "url": "/matches?page=3"}
                ],
                "next_url": "/matches?page=3"
            }
        }
        html_content = self.renderer.render(self.template_name, context)
        soup = BeautifulSoup(html_content, "html.parser")
        pagination = soup.find("div", class_="pagination")
        self.assertIsNotNone(pagination)
        previous_link = pagination.find("a", class_="prev")
        self.assertIsNotNone(previous_link)
        self.assertEqual(previous_link.get("href"), "/matches?page=1")
        page_links = pagination.find_all("a", class_="num-page")
        self.assertEqual(len(page_links), 3)
        self.assertEqual(page_links[0].get("href"), "/matches?page=1")
        self.assertEqual(page_links[1].get("href"), "/matches?page=2")
        self.assertEqual(page_links[2].get("href"), "/matches?page=3")
        next_link = pagination.find("a", class_="next")
        self.assertIsNotNone(next_link)
        self.assertEqual(next_link.get("href"), "/matches?page=3")





























