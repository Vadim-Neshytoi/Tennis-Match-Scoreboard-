import unittest
from unittest.mock import MagicMock
from exceptions.validation_exceptions import DuplicateNamesAfterNormalizationError, InvalidPlayerNameError
from application.application_services.match_creation_service import MatchCreationService


class TestMatchCreationService(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_uow = MagicMock() # создает подмену настоящего объекта. Конкретно тут мы создаём объект-подмену UnitOfWork
        self.mock_uow.__enter__.return_value = self.mock_uow

        self.mock_player_repo = self.mock_uow.player_repo # создаёт дочерний mock для player_repo
        self.mock_match_repo = self.mock_uow.match_repo # создаёт дочерний mock для match_repo

        self.mock_player = MagicMock() # Это подмена настоящего доменного объекта Player.
        self.mock_player_repo.find_or_create_player.return_value = self.mock_player # У любого MagicMock есть свойство return_value.
        # Оно определяет: Что вернёт mock, когда его вызовут. В данном случае вернет подмену настоящего доменного объекта Player

        self.mock_uow_factory = MagicMock()
        self.mock_uow_factory.return_value = self.mock_uow

        self.service = MatchCreationService(self.mock_uow_factory)

    def test_create_match_successfully(self) -> None:
        mock_player1 = MagicMock()
        mock_player2 = MagicMock()
        self.mock_player_repo.find_or_create_player.side_effect = [mock_player1, mock_player2]

        domain_match = self.service.create_match("   Alex   ", " Bob ")

        saved_in_repo_match = self.mock_match_repo.create_match.call_args.args[0]

        self.assertIs(domain_match, saved_in_repo_match)
        self.assertIs(domain_match.player_1, mock_player1)
        self.assertIs(domain_match.player_2, mock_player2)

        players_calls = self.mock_player_repo.find_or_create_player.call_args_list

        self.assertEqual(len(players_calls), 2)
        self.assertEqual(players_calls[0].args[0], "Alex")
        self.assertEqual(players_calls[1].args[0], "Bob")

        self.mock_match_repo.create_match.assert_called_once()
        self.mock_uow.commit.assert_called_once()

    def test_create_match_name_not_validate_name(self) -> None:
        with self.assertRaises(InvalidPlayerNameError):
            self.service.create_match("Alex!", "")
        self.mock_uow_factory.assert_not_called()

    def test_find_or_create_match_identical_name(self) -> None:
        with self.assertRaises(DuplicateNamesAfterNormalizationError):
            self.service.create_match("  Alex", " ALEX ")
        self.mock_uow_factory.assert_not_called()




































