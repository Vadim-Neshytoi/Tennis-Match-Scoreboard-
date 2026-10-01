import unittest
from unittest.mock import MagicMock
from application.application_services.finished_matches_service import FinishedMatchesService
from application.dto.finished_matches_result import FinishedMatchesResult
from exceptions.validation_exceptions import PageNotFoundError
from models.match import Match


class TestFinishedMatchesService(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_uow = MagicMock() # создает подмену настоящего объекта. Конкретно тут мы создаём объект-подмену UnitOfWork
        self.mock_uow.__enter__.return_value = self.mock_uow

        self.mock_match_repo = self.mock_uow.match_repo # создаёт дочерний mock для match_repo

        self.mock_uow_factory = MagicMock()
        self.mock_uow_factory.return_value = self.mock_uow

        self.mock_name_validator = MagicMock()
        self.service = FinishedMatchesService(self.mock_uow_factory, self.mock_name_validator)

    def test_finished_matches_service_not_found_finished_matches(self) -> None:
        page = 1
        player_name = None
        matches = []
        total_count = 0
        self.mock_match_repo.find_finished_matches_page.return_value = (matches, total_count)

        result = self.service.get_finished_matches(page, player_name)

        self.mock_uow.commit.assert_not_called()
        self.assertEqual(result.total_count, 0)
        self.assertEqual(result.matches, [])
        self.assertEqual(result.items_per_page, 10)
        self.assertEqual(result.total_pages, 0)
        self.assertEqual(result.current_page, 1)
        self.assertEqual(result.player_name, None)
        self.assertIsInstance(result, FinishedMatchesResult)

    def test_finished_matches_service_one_finished_matches(self) -> None:
        page = 1
        player_name = None
        match1 = Match(MagicMock(), MagicMock(), MagicMock())
        matches = [match1]
        total_count = 1
        self.mock_match_repo.find_finished_matches_page.return_value = (matches, total_count)

        result = self.service.get_finished_matches(page, player_name)

        self.assertEqual(result.total_count, 1)
        self.assertEqual(result.matches, [match1])
        self.assertEqual(result.items_per_page, 10)
        self.assertEqual(result.total_pages, 1)
        self.assertEqual(result.current_page, 1)
        self.assertEqual(result.player_name, None)
        self.assertIsInstance(result, FinishedMatchesResult)

    def test_finished_matches_service_one_full_page(self) -> None:
        page = 1
        player_name = None
        matches = [MagicMock() for _ in range(10)]
        total_count = 10
        self.mock_match_repo.find_finished_matches_page.return_value = (matches, total_count)

        result = self.service.get_finished_matches(page, player_name)

        self.assertEqual(result.total_count, 10)
        self.assertEqual(len(result.matches), 10)
        self.assertEqual(result.items_per_page, 10)
        self.assertEqual(result.total_pages, 1)
        self.assertEqual(result.current_page, 1)
        self.assertEqual(result.player_name, None)
        self.assertIsInstance(result, FinishedMatchesResult)

    def test_finished_matches_service_calculates_two_pages(self) -> None:
        page = 2
        player_name = None
        matches = [MagicMock() for _ in range(1)]
        total_count = 11
        self.mock_match_repo.find_finished_matches_page.return_value = (matches, total_count)

        result = self.service.get_finished_matches(page, player_name)

        self.assertEqual(result.total_count, 11)
        self.assertEqual(len(result.matches), 1)
        self.assertEqual(result.items_per_page, 10)
        self.assertEqual(result.total_pages, 2)
        self.assertEqual(result.current_page, 2)
        self.assertEqual(result.player_name, None)
        self.assertIsInstance(result, FinishedMatchesResult)

    def test_finished_matches_service_search_name(self) -> None:
        page = 1
        player_name = "  Alex    Smith    "
        matches = [MagicMock() for _ in range(10)]
        total_count = 10
        normalized_name = "Alex Smith"
        self.mock_name_validator.validate_and_normalize_name.return_value = normalized_name
        self.mock_match_repo.find_finished_matches_page.return_value = (matches, total_count)

        result = self.service.get_finished_matches(page, player_name)

        self.mock_name_validator.validate_and_normalize_name.assert_called_once_with(name=player_name,
                                                                                     field_name="filter_by_player_name")
        self.mock_match_repo.find_finished_matches_page.assert_called_once_with(page=page,
                                                                                page_size=self.service._items_per_page,
                                                                                player_name=normalized_name)
        self.assertEqual(result.total_count, 10)
        self.assertEqual(len(result.matches), 10)
        self.assertEqual(result.items_per_page, 10)
        self.assertEqual(result.total_pages, 1)
        self.assertEqual(result.current_page, 1)
        self.assertEqual(result.player_name, normalized_name)
        self.assertIsInstance(result, FinishedMatchesResult)

    def test_finished_matches_service_search_name_none(self) -> None:
        page = 1
        player_name = None
        matches = [MagicMock() for _ in range(10)]
        total_count = 10
        self.mock_match_repo.find_finished_matches_page.return_value = (matches, total_count)

        result = self.service.get_finished_matches(page, player_name)

        self.mock_match_repo.find_finished_matches_page.assert_called_once_with(page=page,
                                                                                page_size=self.service._items_per_page,
                                                                                player_name=player_name)
        self.mock_name_validator.validate_and_normalize_name.assert_not_called()
        self.assertEqual(result.total_count, 10)
        self.assertEqual(len(result.matches), 10)
        self.assertEqual(result.items_per_page, 10)
        self.assertEqual(result.total_pages, 1)
        self.assertEqual(result.current_page, 1)
        self.assertEqual(result.player_name, player_name)

    def test_finished_matches_service_custom_items_per_page(self) -> None:
        page = 2
        player_name = None
        matches = [MagicMock() for _ in range(5)]
        total_count = 11
        self.service =  FinishedMatchesService(self.mock_uow_factory, self.mock_name_validator, items_per_page=5)
        self.mock_match_repo.find_finished_matches_page.return_value = (matches, total_count)

        result = self.service.get_finished_matches(page, player_name)

        self.assertEqual(result.total_count, 11)
        self.assertEqual(len(result.matches), 5)
        self.assertEqual(result.items_per_page, 5)
        self.assertEqual(result.total_pages, 3)
        self.assertEqual(result.current_page, 2)
        self.assertEqual(result.player_name, None)
        self.assertIsInstance(result, FinishedMatchesResult)
        self.mock_match_repo.find_finished_matches_page.assert_called_once_with(page=page,
                                                                                page_size=self.service._items_per_page,
                                                                                player_name=player_name)

    def test_finished_matches_page_not_found(self) -> None:
        page = 3
        player_name = None
        matches = []
        total_count = 11
        self.mock_match_repo.find_finished_matches_page.return_value = (matches, total_count)

        with self.assertRaises(PageNotFoundError):
            self.service.get_finished_matches(page, player_name)

    def test_finished_matches_page_empty(self) -> None:
        page = 999
        player_name = None
        matches = []
        total_count = 0
        self.mock_match_repo.find_finished_matches_page.return_value = (matches, total_count)

        result = self.service.get_finished_matches(page, player_name)

        self.assertEqual(result.total_count, 0)
        self.assertEqual(len(result.matches), 0)
        self.assertEqual(result.items_per_page, 10)
        self.assertEqual(result.total_pages, 0)
        self.assertEqual(result.current_page, 1)
        self.assertEqual(result.player_name, None)
        self.assertIsInstance(result, FinishedMatchesResult)
        self.mock_match_repo.find_finished_matches_page.assert_called_once_with(page=page,
                                                                                page_size=self.service._items_per_page,
                                                                                player_name=None)

































