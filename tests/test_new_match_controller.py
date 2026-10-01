import unittest
from unittest.mock import MagicMock
from werkzeug.test import EnvironBuilder # noqa
from werkzeug.wrappers import Response, Request # noqa
from application.application_services.match_creation_service import MatchCreationService
from exceptions.validation_exceptions import InvalidPlayerNameError, DuplicateNamesAfterNormalizationError
from controllers.new_match_controller import NewMatchController
from models.match import Match
from models.player import Player
from presentation.template_renderer import TemplateRenderer


class TestNewMatchController(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = MagicMock(spec=TemplateRenderer)
        self.service = MagicMock(spec=MatchCreationService)
        self.controller = NewMatchController(self.service, self.renderer)


    @staticmethod
    def make_create_match_request(form_data: dict[str, str]) -> Request:
        builder = EnvironBuilder(
            path="/new-match",
            method="POST",
            data=form_data
        )
        return Request(builder.get_environ()) # возвращает WSGI environ который обычно получает от Waitress, но вместо
    # Waitress мы создаём environ через EnvironBuilder, а после Werkzeug получает WSGI environ и создаёт удобный объект: Request

    @staticmethod
    def make_show_form_request() -> Request:
        builder = EnvironBuilder(
            path="/new-match",
            method="GET",
        )
        return Request(builder.get_environ())

    def test_new_match_controller_create_match_player1_absent(self) -> None:
        payload = {"player_2_name" : "Bob"}
        request = self.make_create_match_request(payload)
        view_data = {
            "player_1_name": None,
            "player_2_name": "Bob",
            "error": {"field": "player1",
                      "message": "Введите имя игрока"}
        }
        expected_html = "<html><body>New Match Form</body></html>"
        self.renderer.render.return_value = expected_html
        result = self.controller.create_match(request)
        actual_html = result.get_data(as_text=True)

        self.renderer.render.assert_called_once_with("new-match.html", view_data)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(actual_html, expected_html)
        self.assertEqual(result.mimetype, "text/html")
        self.service.create_match.assert_not_called()

    def test_new_match_controller_create_match_player2_absent(self) -> None:
        payload = {"player_1_name" : "Alex"}
        request = self.make_create_match_request(payload)
        view_data = {
            "player_1_name": "Alex",
            "player_2_name": None,
            "error": {"field": "player2",
                      "message": "Введите имя игрока"}
        }
        expected_html = "<html><body>New Match Form</body></html>"
        self.renderer.render.return_value = expected_html
        result = self.controller.create_match(request)
        actual_html = result.get_data(as_text=True)

        self.renderer.render.assert_called_once_with("new-match.html", view_data)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(actual_html, expected_html)
        self.assertEqual(result.mimetype, "text/html")
        self.service.create_match.assert_not_called()


    def test_new_match_controller_create_match_player1_invalid(self) -> None:
        payload = {"player_1_name" : "Al ex lait", "player_2_name" : "Bob"}
        request = self.make_create_match_request(payload)
        self.service.create_match.side_effect = InvalidPlayerNameError(field_name="player1",
                                                                       message="Имя может содержать не более двух слов")
        view_data = {
            "player_1_name": "Al ex lait",
            "player_2_name": "Bob",
            "error": {"field": "player1",
                      "message": "Имя может содержать не более двух слов"}
        }
        expected_html = "<html><body>New Match Form</body></html>"
        self.renderer.render.return_value = expected_html
        result = self.controller.create_match(request)
        actual_html = result.get_data(as_text=True)

        self.renderer.render.assert_called_once_with("new-match.html", view_data)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(actual_html, expected_html)
        self.assertEqual(result.mimetype, "text/html")
        self.service.create_match.assert_called_once_with("Al ex lait", "Bob")

    def test_new_match_controller_create_match_player2_invalid(self) -> None:
        payload = {"player_1_name" : "Alex", "player_2_name" : "B"}
        request = self.make_create_match_request(payload)
        self.service.create_match.side_effect = InvalidPlayerNameError(field_name="player2",
                                                                       message="Имя должно содержать от 2 до 30 символов")
        view_data = {
            "player_1_name": "Alex",
            "player_2_name": "B",
            "error": {"field": "player2",
                      "message": "Имя должно содержать от 2 до 30 символов"}
        }
        expected_html = "<html><body>New Match Form</body></html>"
        self.renderer.render.return_value = expected_html
        result = self.controller.create_match(request)
        actual_html = result.get_data(as_text=True)

        self.renderer.render.assert_called_once_with("new-match.html", view_data)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(actual_html, expected_html)
        self.assertEqual(result.mimetype, "text/html")
        self.service.create_match.assert_called_once_with("Alex", "B")

    def test_new_match_controller_create_match_duplicate_name(self) -> None:
        payload = {"player_1_name" : "alex", "player_2_name" : "ALEX"}
        request = self.make_create_match_request(payload)
        self.service.create_match.side_effect = DuplicateNamesAfterNormalizationError(message="Имена игроков должны различаться")
        view_data = {
            "player_1_name": "alex",
            "player_2_name": "ALEX",
            "error": {"field": None,
                      "message": "Имена игроков должны различаться"}
        }
        expected_html = "<html><body>New Match Form</body></html>"
        self.renderer.render.return_value = expected_html
        result = self.controller.create_match(request)
        actual_html = result.get_data(as_text=True)

        self.renderer.render.assert_called_once_with("new-match.html", view_data)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(actual_html, expected_html)
        self.assertEqual(result.mimetype, "text/html")
        self.service.create_match.assert_called_once_with("alex", "ALEX")

    def test_new_match_controller_create_match_successful(self) -> None:
        payload = {"player_1_name" : "Alex", "player_2_name" : "Bob"}
        request = self.make_create_match_request(payload)
        player1 = Player("Alex", 1)
        player2 = Player("Bob", 2)
        test_match = Match(player1, player2)
        self.service.create_match.return_value = test_match

        result = self.controller.create_match(request)
        location = result.headers.get("Location")


        self.assertEqual(location, f"/match-score?uuid={test_match.uuid}")
        self.assertEqual(result.status_code, 303)
        self.service.create_match.assert_called_once_with("Alex", "Bob")

    def test_show_form(self) -> None:
        view_data = {
            "player_1_name": "",
            "player_2_name": "",
            "error": None,
        }
        expected_html = "<html><body>New Match Form</body></html>"
        self.renderer.render.return_value = expected_html
        result = self.controller.show_form(self.make_show_form_request())

        self.renderer.render.assert_called_once_with("new-match.html", view_data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.mimetype, "text/html")

        actual_html = result.get_data(as_text=True)
        self.assertEqual(actual_html, expected_html)


