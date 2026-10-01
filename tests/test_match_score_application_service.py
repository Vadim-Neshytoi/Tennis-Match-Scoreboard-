import unittest
from unittest.mock import MagicMock
from application.application_services.match_score_application_service import MatchScoreApplicationService
from exceptions.validation_exceptions import MatchNotFoundError, PlayerNotInMatchError


class TestMatchScoreApplicationService(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_uow = MagicMock() # создает подмену настоящего объекта. Конкретно тут мы создаём объект-подмену UnitOfWork
        self.mock_uow.__enter__.return_value = self.mock_uow

        self.mock_match_repo = self.mock_uow.match_repo # создаёт дочерний mock для match_repo

        self.mock_uow_factory = MagicMock()
        self.mock_uow_factory.return_value = self.mock_uow
        self.score_service = MagicMock()

        self.service = MatchScoreApplicationService(self.mock_uow_factory, self.score_service)


    def test_match_score_application_service_match_continues(self) -> None:
        player_1_id = 1
        player_2_id = 2
        mock_player = MagicMock()

        mock_match_domain_model = MagicMock()
        mock_match_domain_model.player_1 = MagicMock(id=player_1_id)
        mock_match_domain_model.player_2 = MagicMock(id=player_2_id)

        self.mock_match_repo.find_match_by_uuid.return_value = mock_match_domain_model
        mock_match_domain_model.get_player_by_id.return_value = mock_player
        self.score_service.play_match.return_value = None
        mock_match_domain_model.winner = None

        result = self.service.play_match(mock_match_domain_model.uuid, player_1_id)

        self.assertEqual(result, mock_match_domain_model)
        self.mock_match_repo.update.assert_called_once_with(mock_match_domain_model)
        self.score_service.play_match.assert_called_once_with(mock_match_domain_model, mock_player)
        self.mock_uow.commit.assert_called_once()
        self.assertEqual(mock_match_domain_model.winner, None)


    def test_match_score_application_service_match_none(self) -> None:
        player_1_id = 1
        test_uuid = "test_uuid"

        mock_match_domain_model = MagicMock()
        self.mock_match_repo.find_match_by_uuid.return_value = None

        with self.assertRaises(MatchNotFoundError):
            self.service.play_match(test_uuid, player_1_id)

        self.score_service.play_match.assert_not_called()
        self.mock_match_repo.find_match_by_uuid.assert_called_once_with(test_uuid)
        self.mock_match_repo.update.assert_not_called()
        self.mock_uow.commit.assert_not_called()
        mock_match_domain_model.get_player_by_id.assert_not_called()

    def test_match_score_application_service_sets_winner(self) -> None:
        player_1_id = 1
        player_2_id = 2
        mock_player = MagicMock()
        test_uuid = "test_uuid"

        mock_match_domain_model = MagicMock()
        mock_match_domain_model.player_1 = MagicMock(id=player_1_id)
        mock_match_domain_model.player_2 = MagicMock(id=player_2_id)
        mock_match_domain_model.winner = None

        self.mock_match_repo.find_match_by_uuid.return_value = mock_match_domain_model
        mock_match_domain_model.get_player_by_id.return_value = mock_player
        self.score_service.play_match.return_value = mock_player

        result = self.service.play_match(test_uuid, player_1_id)

        self.assertEqual(result, mock_match_domain_model)
        self.mock_match_repo.update.assert_called_once_with(mock_match_domain_model)
        self.mock_match_repo.find_match_by_uuid.assert_called_once_with(test_uuid)
        self.score_service.play_match.assert_called_once_with(mock_match_domain_model, mock_player)
        self.mock_uow.commit.assert_called_once()
        self.assertEqual(result.winner, mock_player)
        mock_match_domain_model.get_player_by_id.assert_called_once_with(player_1_id)

    def test_match_score_application_service_player_not_found(self) -> None:
        player_1_id = 1
        player_2_id = 2

        mock_match_domain_model = MagicMock()
        mock_match_domain_model.player_1 = MagicMock(id=player_1_id)
        mock_match_domain_model.player_2 = MagicMock(id=player_2_id)

        self.mock_match_repo.find_match_by_uuid.return_value = mock_match_domain_model
        mock_match_domain_model.get_player_by_id.side_effect = PlayerNotInMatchError("Данный игрок в этом матче не учавствует")
        self.score_service.play_match.return_value = None

        with self.assertRaises(PlayerNotInMatchError):
            self.service.play_match(mock_match_domain_model.uuid, 5)

        self.mock_match_repo.find_match_by_uuid.assert_called_once_with(mock_match_domain_model.uuid)
        mock_match_domain_model.get_player_by_id.assert_called_once_with(5)
        self.score_service.play_match.assert_not_called()
        self.mock_match_repo.update.assert_not_called()
        self.mock_uow.commit.assert_not_called()










































