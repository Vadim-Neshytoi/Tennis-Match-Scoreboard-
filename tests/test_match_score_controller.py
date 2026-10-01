import json
import unittest
from uuid import uuid4
from unittest.mock import MagicMock
from werkzeug.test import EnvironBuilder # noqa
from werkzeug.wrappers import Response, Request # noqa
from application.application_services.match_query_service import MatchQueryService
from application.application_services.match_score_application_service import MatchScoreApplicationService
from controllers.match_score_controller import MatchScoreController
from exceptions.validation_exceptions import MatchNotFoundError, PlayerNotInMatchError
from mappers.match_view_mapper import MatchViewMapper
from models.match import Match
from models.player import Player
from presentation.template_renderer import TemplateRenderer


class TestMatchScoreController(unittest.TestCase):

    def setUp(self) -> None:
        self.renderer = MagicMock(spec=TemplateRenderer)
        self.match_query_service = MagicMock(spec=MatchQueryService)
        self.match_score_app_service = MagicMock(spec=MatchScoreApplicationService)
        self.mapper = MagicMock(spec=MatchViewMapper)
        self.controller = MatchScoreController(self.renderer, self.match_query_service, self.match_score_app_service, self.mapper)

    @staticmethod
    def make_show_score_request(query_params: dict[str, str | None]) -> Request:
        builder = EnvironBuilder(
            path="/match-score",
            method="GET",
            query_string=query_params,
        )
        return Request(builder.get_environ())

    @staticmethod
    def make_update_score_request(query_params: dict[str, str | None], data_params: dict[str, str | None]) -> Request:
        builder = EnvironBuilder(
            path="/match-score",
            method="POST",
            query_string=query_params,
            data=data_params
        )
        return Request(builder.get_environ())

    def test_match_score_controller_show_score_uuid_invalid(self) -> None:
        expected_response = {"error": "Параметр uuid обязателен для передачи и не может быть пустым"}
        cases = [
            None,
            "",
            "     "
        ]
        for uuid in cases:
            with self.subTest(f"Проверка отсутствия или неверного формата uuid:{uuid}"):
                request = self.make_show_score_request({"uuid": uuid})
                result = self.controller.show_score(request)
                response_text = json.loads(result.get_data(as_text=True))

                self.assertEqual(result.status_code, 400)
                self.assertEqual(result.mimetype, 'application/json')
                self.assertEqual(response_text, expected_response)
                self.match_query_service.get_match_by_uuid.assert_not_called()
                self.mapper.to_view_data.assert_not_called()
                self.renderer.render.assert_not_called()

    def test_match_score_controller_show_score_match_not_found(self) -> None:
        uuid = str(uuid4())
        request = self.make_show_score_request({"uuid": uuid})
        self.match_query_service.get_match_by_uuid.side_effect = MatchNotFoundError("Матч не найден")
        expected_response = {"error": "Ошибка: Матч не найден"}

        result = self.controller.show_score(request)
        response_text = json.loads(result.get_data(as_text=True))

        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.mimetype, "application/json")
        self.assertEqual(response_text, expected_response)
        self.match_query_service.get_match_by_uuid.assert_called_once_with(uuid)
        self.mapper.to_view_data.assert_not_called()
        self.renderer.render.assert_not_called()

    def test_match_score_controller_show_score_success(self) -> None:
        player1 = Player(name="Alex", ID=1)
        player2 = Player(name="Bob", ID=2)
        domain_match = Match(player1, player2, winner=player1)
        test_uuid = str(uuid4())
        self.match_query_service.get_match_by_uuid.return_value = domain_match
        test_mapped_data = {
            "uuid": test_uuid,
            "player1": {"name": "Alex",
                        "id": 1,
                        "points": "0",
                        "games": 0,
                        "sets": 2},
            "player2": {"name": "Bob",
                        "id": 2,
                        "points": "0",
                        "games": 0,
                        "sets": 1},
            "winner": player1.name
        }
        self.mapper.to_view_data.return_value = test_mapped_data
        expected_html = "<html><body>Alex vs Bob</html></body>"
        self.renderer.render.return_value = expected_html
        request = self.make_show_score_request({"uuid": test_uuid})
        result = self.controller.show_score(request)

        cleaned_uuid = test_uuid.strip()
        self.match_query_service.get_match_by_uuid.assert_called_once_with(cleaned_uuid)
        self.mapper.to_view_data.assert_called_once_with(domain_match)
        self.renderer.render.assert_called_once_with("match-score.html", test_mapped_data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.mimetype, "text/html")

        actual_html = result.get_data(as_text=True)
        self.assertEqual(actual_html, expected_html)

    def test_show_score_strips_uuid(self) -> None:
        request = self.make_show_score_request({"uuid": "   abc-uuid    "})
        cleaned_uuid = "abc-uuid"
        self.controller.show_score(request)

        self.match_query_service.get_match_by_uuid.assert_called_once_with(cleaned_uuid)

    def test_update_score_uuid_invalid(self) -> None:
        expected_response = {"error": "Параметр uuid обязателен для передачи и не может быть пустым"}
        cases = [
            None,
            "",
            "     "
        ]
        for uuid in cases:
            with self.subTest(f"Проверка отсутствия или неверного формата uuid:{uuid}"):
                request = self.make_update_score_request({"uuid": uuid}, {"player_id": "1"})
                result = self.controller.update_score(request)
                response_text = json.loads(result.get_data(as_text=True))

                self.assertEqual(result.status_code, 400)
                self.assertEqual(result.mimetype, "application/json")
                self.assertEqual(response_text, expected_response)
                self.match_score_app_service.play_match.assert_not_called()
                self.mapper.to_view_data.assert_not_called()
                self.renderer.render.assert_not_called()

    def test_update_score_player_id_invalid(self) -> None:
        expected_response = {"error": "Параметр player_id обязателен для передачи и не может быть пустым"}
        cases = [
            None,
            "",
            "     "
        ]
        for player_id in cases:
            with self.subTest(f"Проверка отсутствия или неверного формата player_id:{player_id}"):
                request = self.make_update_score_request({"uuid": "abc-675_kkk"}, {"player_id": player_id})
                result = self.controller.update_score(request)
                response_text = json.loads(result.get_data(as_text=True))

                self.assertEqual(result.status_code, 400)
                self.assertEqual(result.mimetype, 'application/json')
                self.assertEqual(response_text, expected_response)
                self.match_score_app_service.play_match.assert_not_called()
                self.mapper.to_view_data.assert_not_called()
                self.renderer.render.assert_not_called()

    def test_update_score_player_id_not_int(self) -> None:
        expected_response = {"error": "Параметр player_id должен быть исключительно числом"}
        cases = [
            "abc",
            "12.5",
        ]
        for player_id in cases:
            with self.subTest(f"Проверка отсутствия или неверного формата player_id:{player_id}"):
                request = self.make_update_score_request({"uuid": "abc-675_kkk"}, {"player_id": player_id})
                result = self.controller.update_score(request)
                response_text = json.loads(result.get_data(as_text=True))

                self.assertEqual(result.status_code, 400)
                self.assertEqual(result.mimetype, "application/json")
                self.assertEqual(response_text, expected_response)
                self.match_score_app_service.play_match.assert_not_called()
                self.mapper.to_view_data.assert_not_called()
                self.renderer.render.assert_not_called()

    def test_update_score_player_match_not_found(self) -> None:
        expected_response = {"error": "Ошибка: Матч не найден"}
        request = self.make_update_score_request({"uuid": "abc-675_kkk"}, {"player_id": "1"})
        self.match_score_app_service.play_match.side_effect = MatchNotFoundError("Матч не найден")

        result = self.controller.update_score(request)
        response_text = json.loads(result.get_data(as_text=True))

        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.mimetype, "application/json")
        self.assertEqual(response_text, expected_response)
        self.mapper.to_view_data.assert_not_called()
        self.renderer.render.assert_not_called()

    def test_update_score_player_player_not_play_match(self) -> None:
        expected_response = {"error": "Ошибка: Данный игрок в этом матче не учавствует"}
        request = self.make_update_score_request({"uuid": "abc-675_kkk"}, {"player_id": "1"})
        self.match_score_app_service.play_match.side_effect = PlayerNotInMatchError("Данный игрок в этом матче не учавствует")

        result = self.controller.update_score(request)
        response_text = json.loads(result.get_data(as_text=True))

        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.mimetype, "application/json")
        self.assertEqual(response_text, expected_response)
        self.mapper.to_view_data.assert_not_called()
        self.renderer.render.assert_not_called()

    def test_update_score_player_match_continue(self) -> None:
        player1 = Player("Alex", 1)
        player2 = Player("Bob", 2)
        test_match = Match(player1, player2, winner=None)
        request = self.make_update_score_request({"uuid": test_match.uuid}, {"player_id": "1"})
        cleaned_uuid = test_match.uuid.strip()
        player_id_int = int("1")
        self.match_score_app_service.play_match.return_value = test_match

        result = self.controller.update_score(request)
        location = result.headers.get("Location")

        self.match_score_app_service.play_match.assert_called_once_with(cleaned_uuid, player_id_int)
        self.assertEqual(location, f"/match-score?uuid={test_match.uuid}")
        self.assertEqual(result.status_code, 303)
        self.mapper.to_view_data.assert_not_called()
        self.renderer.render.assert_not_called()

    def test_update_score_player_match_finished(self) -> None:
        player1 = Player("Alex", 1)
        player2 = Player("Bob", 2)
        test_match = Match(player1, player2, winner=player1)
        request = self.make_update_score_request({"uuid": test_match.uuid}, {"player_id": "1"})
        cleaned_uuid = test_match.uuid.strip()
        player_id_int = int("1")
        self.match_score_app_service.play_match.return_value = test_match

        result = self.controller.update_score(request)

        self.match_score_app_service.play_match.assert_called_once_with(cleaned_uuid, player_id_int)
        self.assertEqual(result.status_code, 303)
        self.assertEqual(result.headers["Location"], f"/match-score?uuid={test_match.uuid}")














































