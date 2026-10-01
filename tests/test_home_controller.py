import unittest
from unittest.mock import MagicMock
from werkzeug.test import EnvironBuilder # noqa
from werkzeug.wrappers import Response, Request # noqa
from controllers.home_controller import HomeController
from presentation.template_renderer import TemplateRenderer


class TestHomeController(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = MagicMock(spec=TemplateRenderer)
        self.controller = HomeController(self.renderer)

    @staticmethod
    def make_show_home_request() -> Request:
        builder = EnvironBuilder(
            path="/new-match",
            method="GET",
        )
        return Request(builder.get_environ())

    def test_show_home(self) -> None:
        expected_html = "<html><body>Home Form</body></html>"
        self.renderer.render.return_value = expected_html
        result = self.controller.show_home(self.make_show_home_request())

        self.renderer.render.assert_called_once_with("index.html", {})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.mimetype, "text/html")

        actual_html = result.get_data(as_text=True)
        self.assertEqual(actual_html, expected_html)