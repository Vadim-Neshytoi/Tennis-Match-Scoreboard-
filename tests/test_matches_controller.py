import json
import unittest
from unittest.mock import MagicMock
from werkzeug.test import EnvironBuilder # noqa
from werkzeug.wrappers import Response, Request # noqa
from application.application_services.finished_matches_service import FinishedMatchesService
from application.dto.finished_matches_result import FinishedMatchesResult
from controllers.matches_controller import MatchesController
from exceptions.validation_exceptions import InvalidPageError, InvalidPlayerNameError, PageNotFoundError
from mappers.finished_match_view_mapper import FinishedMatchViewMapper
from presentation.template_renderer import TemplateRenderer
from validators.page_validator import PageValidator


class TestMatchesController(unittest.TestCase):

    def setUp(self):
        self.services = MagicMock(spec=FinishedMatchesService)
        self.mapper = MagicMock(spec=FinishedMatchViewMapper)
        self.page_validator = MagicMock(spec=PageValidator)
        self.renderer = MagicMock(spec=TemplateRenderer)

        self.matches_controller = MatchesController(self.services, self.mapper, self.page_validator, self.renderer)

    @staticmethod
    def make_show_finished_matches_request(page: str | int | None, player_name: str | None) -> Request:
        query_params = {'page': page, 'filter_by_player_name': player_name}
        builder = EnvironBuilder(
            path="/matches",
            method="GET",
            query_string=query_params,
        )
        return Request(builder.get_environ())

    def test_matches_controller_empty_page(self):
        player_name = None
        cases = [
            None,
            "",
            "      "
        ]
        expected_html = "<html><body> Alex Bob Alex </body></html>"
        self.renderer.render.return_value = expected_html
        for page in cases:
            with self.subTest(f"Проверка отсутствия или пустого параметра page:{page}"):
                request = self.make_show_finished_matches_request(page=page, player_name=player_name)
                result = self.matches_controller.show_finished_matches(request)

                self.page_validator.validate_page.assert_called_once_with("1")
                self.services.get_finished_matches.assert_called_once()
                self.mapper.to_view_data.assert_called_once()
                self.renderer.render.assert_called_once()
                self.assertEqual(result.status_code, 200)
                self.assertEqual(result.mimetype, "text/html")
                self.assertEqual(result.get_data(as_text=True), expected_html)

                self.page_validator.validate_page.reset_mock()
                self.services.get_finished_matches.reset_mock()
                self.mapper.to_view_data.reset_mock()
                self.renderer.render.reset_mock()

    def test_matches_controller_invalid_page(self):
        expected_response = {"error": "Страница должна быть исключительно числом и больше 0"}
        player_name = None
        cases = [
            "abc",
            "0",
            "-21"
            "$1$"
        ]
        self.page_validator.validate_page.side_effect = InvalidPageError()
        for page in cases:
            with self.subTest(f"Проверка неверного параметра page:{page}"):
                request = self.make_show_finished_matches_request(page=page, player_name=player_name)
                result = self.matches_controller.show_finished_matches(request)
                response_text = json.loads(result.get_data(as_text=True))

                self.page_validator.validate_page.assert_called_once_with(page)
                self.services.get_finished_matches.assert_not_called()
                self.mapper.to_view_data.assert_not_called()
                self.renderer.render.assert_not_called()
                self.assertEqual(result.status_code, 400)
                self.assertEqual(result.mimetype, "application/json")
                self.assertEqual(response_text, expected_response)

                self.page_validator.validate_page.reset_mock()

    def test_matches_controller_player_name_empty(self):
        page = 1
        cases = [
            None,
            "",
            "    "
        ]
        expected_html = "<html><body> Alex Bob Alex </body></html>"
        self.renderer.render.return_value = expected_html
        self.page_validator.validate_page.return_value = 1
        for name in cases:
            with self.subTest(f"Проверка отсутствия или пустого параметра name:{name}"):
                request = self.make_show_finished_matches_request(page=page, player_name=name)
                result = self.matches_controller.show_finished_matches(request)

            self.page_validator.validate_page.assert_called_once_with("1")
            self.services.get_finished_matches.assert_called_once_with(1, None)
            self.mapper.to_view_data.assert_called_once()
            self.renderer.render.assert_called_once()
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.mimetype, "text/html")
            self.assertEqual(result.get_data(as_text=True), expected_html)

            self.page_validator.validate_page.reset_mock()
            self.services.get_finished_matches.reset_mock()
            self.mapper.to_view_data.reset_mock()
            self.renderer.render.reset_mock()

    def test_matches_controller_player_name_not_empty(self):
        page = 1
        name = "    Alex   Smith    "
        expected_html = "<html><body> Alex Bob Alex </body></html>"
        self.renderer.render.return_value = expected_html
        self.page_validator.validate_page.return_value = 1
        request = self.make_show_finished_matches_request(page=page, player_name=name)
        result = self.matches_controller.show_finished_matches(request)

        self.page_validator.validate_page.assert_called_once_with("1")
        self.services.get_finished_matches.assert_called_once_with(1, "    Alex   Smith    ")
        self.mapper.to_view_data.assert_called_once()
        self.renderer.render.assert_called_once()
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.mimetype, "text/html")
        self.assertEqual(result.get_data(as_text=True), expected_html)

    def test_matches_controller_invalid_player_name(self):
        expected_response = {"error": "Ошибка в поле AL EX SM ITH : Имя состоит более чем из двух частей"}
        page = 1
        name = "AL EX SM ITH"
        expected_html = "<html><body> Alex Bob Alex </body></html>"
        self.renderer.render.return_value = expected_html
        self.page_validator.validate_page.return_value = 1
        self.services.get_finished_matches.side_effect = InvalidPlayerNameError(name,
                                                                                "Имя состоит более чем из двух частей")

        request = self.make_show_finished_matches_request(page=page, player_name=name)
        result = self.matches_controller.show_finished_matches(request)
        response_text = json.loads(result.get_data(as_text=True))

        self.page_validator.validate_page.assert_called_once_with("1")
        self.services.get_finished_matches.assert_called_once_with(1, name)
        self.mapper.to_view_data.assert_not_called()
        self.renderer.render.assert_not_called()
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.mimetype, "application/json")
        self.assertEqual(response_text, expected_response)

    def test_matches_controller_page_not_found(self):
        expected_response = {"error": "Страница не найдена"}
        page = 999
        name = "ALEX"
        expected_html = "<html><body> Alex Bob Alex </body></html>"
        self.renderer.render.return_value = expected_html
        self.page_validator.validate_page.return_value = 999
        self.services.get_finished_matches.side_effect = PageNotFoundError()

        request = self.make_show_finished_matches_request(page=page, player_name=name)
        result = self.matches_controller.show_finished_matches(request)
        response_text = json.loads(result.get_data(as_text=True))

        self.page_validator.validate_page.assert_called_once_with("999")
        self.services.get_finished_matches.assert_called_once_with(999, name)
        self.mapper.to_view_data.assert_not_called()
        self.renderer.render.assert_not_called()
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.mimetype, "application/json")
        self.assertEqual(response_text, expected_response)

    def test_matches_controller_success_without_filter(self):
        page = None
        name = None
        finished_matches_result = MagicMock(spec=FinishedMatchesResult)
        mapped_data = {}
        expected_html = "<html><body> Bob Alex Alex </body></html>"
        self.page_validator.validate_page.return_value = 1
        self.services.get_finished_matches.return_value = finished_matches_result
        self.mapper.to_view_data.return_value = mapped_data
        self.renderer.render.return_value = expected_html

        request = self.make_show_finished_matches_request(page=page, player_name=name)
        result = self.matches_controller.show_finished_matches(request)

        self.page_validator.validate_page.assert_called_once_with("1")
        self.services.get_finished_matches.assert_called_once_with(1, name)
        self.mapper.to_view_data.assert_called_once_with(finished_matches_result)
        self.renderer.render.assert_called_once_with("matches.html", mapped_data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.mimetype, "text/html")
        self.assertEqual(result.get_data(as_text=True), expected_html)

    def test_matches_controller_success_with_filter(self):
        page = 2
        name = "Alex"
        finished_matches_result = MagicMock(spec=FinishedMatchesResult)
        mapped_data = {}
        expected_html = "<html><body> Bob Alex Alex </body></html>"
        self.page_validator.validate_page.return_value = 2
        self.services.get_finished_matches.return_value = finished_matches_result
        self.mapper.to_view_data.return_value = mapped_data
        self.renderer.render.return_value = expected_html

        request = self.make_show_finished_matches_request(page=page, player_name=name)
        result = self.matches_controller.show_finished_matches(request)

        self.page_validator.validate_page.assert_called_once_with("2")
        self.services.get_finished_matches.assert_called_once_with(2, "Alex")
        self.mapper.to_view_data.assert_called_once_with(finished_matches_result)
        self.renderer.render.assert_called_once_with("matches.html", mapped_data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.mimetype, "text/html")
        self.assertEqual(result.get_data(as_text=True), expected_html)



































