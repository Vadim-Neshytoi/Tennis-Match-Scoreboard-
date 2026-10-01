import unittest
from unittest.mock import MagicMock
from werkzeug.wrappers import Response, Request  # noqa
from werkzeug.test import EnvironBuilder # noqa
from werkzeug.utils import redirect # noqa
from werkzeug.datastructures import Headers # noqa
from wsgiref.validate import validator

from controllers.home_controller import HomeController
from controllers.match_score_controller import MatchScoreController
from controllers.matches_controller import MatchesController
from controllers.new_match_controller import NewMatchController
from wsgi_application.static_file_handler import StaticFileHandler
from wsgi_application.wsgi_application import WSGIApplication


class TestWSGIApplication(unittest.TestCase):

    def setUp(self) -> None:
        self.new_match_controller = MagicMock(spec=NewMatchController)
        self.match_score_controller = MagicMock(spec=MatchScoreController)
        self.matches_controller = MagicMock(spec=MatchesController)
        self.home_controller = MagicMock(spec=HomeController)
        self.file_handler = MagicMock(spec=StaticFileHandler)
        self.wsgi_application = WSGIApplication(self.new_match_controller, self.match_score_controller, self.matches_controller,
                                                self.home_controller, self.file_handler)
        self.start_response_mock = MagicMock()
        self.wrapped_app = validator(self.wsgi_application)

    def test_wsgi_application_home_show_home(self) -> None:
        expected_response = Response("Home Form", status=200, mimetype="text/html")
        self.home_controller.show_home.return_value = expected_response
        builder = EnvironBuilder(path="/", method="GET")
        environ = builder.get_environ()
        response_iterable = self.wrapped_app(environ, self.start_response_mock)
        try:
            response_body = b"".join(response_iterable)
        finally:
            if hasattr(response_iterable, "close"):
                response_iterable.close()

        self.home_controller.show_home.assert_called_once()
        called_args, _ = self.home_controller.show_home.call_args
        passed_request = called_args[0]
        self.assertIsInstance(passed_request, Request)
        self.assertEqual(passed_request.method, "GET")
        self.assertEqual(passed_request.path, "/")
        self.start_response_mock.assert_called_once()
        status, headers = self.start_response_mock.call_args[0]
        wsgi_headers = Headers(headers)
        content_type = wsgi_headers.get("Content-Type")
        self.assertEqual(status, "200 OK")
        self.assertEqual(content_type, 'text/html; charset=utf-8')
        self.assertEqual(response_body, b"Home Form")

    def test_wsgi_application_new_match_show_form(self) -> None:
        expected_response = Response("Match Form", status=200, mimetype="text/html")
        self.new_match_controller.show_form.return_value = expected_response
        builder = EnvironBuilder(path="/new-match", method="GET") # EnvironBuilder позволяет в тесте сымитировать
        # HTTP-запрос, из которого Werkzeug затем создаст Request.
        environ = builder.get_environ() # Теперь Werkzeug создаёт WSGI environ и получается полноценный объект запроса
        response_iterable = self.wrapped_app(environ, self.start_response_mock)
        try:
            response_body = b"".join(response_iterable)
        finally:
            if hasattr(response_iterable, "close"):
                response_iterable.close()

        self.new_match_controller.show_form.assert_called_once()
        called_args, _ = self.new_match_controller.show_form.call_args
        passed_request = called_args[0]
        self.assertIsInstance(passed_request, Request)
        self.assertEqual(passed_request.method, "GET")
        self.assertEqual(passed_request.path, "/new-match")
        self.start_response_mock.assert_called_once()
        status, headers = self.start_response_mock.call_args[0]
        wsgi_headers = Headers(headers)
        content_type = wsgi_headers.get("Content-Type")
        self.assertEqual(status, "200 OK")
        self.assertEqual(content_type, 'text/html; charset=utf-8')
        self.assertEqual(response_body, b"Match Form")

    def test_wsgi_application_new_match_create_match(self) -> None:
        expected_response = redirect("/match-score?uuid=123e4567-e89b", code=303)
        self.new_match_controller.create_match.return_value = expected_response
        builder = EnvironBuilder(path="/new-match", method="POST")
        environ = builder.get_environ()
        response_iterable = self.wrapped_app(environ, self.start_response_mock)
        try:
            response_body = b"".join(response_iterable)
        finally:
            if hasattr(response_iterable, "close"):
                response_iterable.close()

        self.new_match_controller.create_match.assert_called_once()
        called_args, _ = self.new_match_controller.create_match.call_args
        passed_request = called_args[0]
        self.assertIsInstance(passed_request, Request)
        self.assertEqual(passed_request.method, "POST")
        self.assertEqual(passed_request.path, "/new-match")
        self.start_response_mock.assert_called_once()
        status, headers = self.start_response_mock.call_args[0]
        wsgi_headers = Headers(headers)
        location = wsgi_headers.get("Location")
        self.assertEqual(status, "303 SEE OTHER")
        self.assertEqual(location, '/match-score?uuid=123e4567-e89b')

    def test_wsgi_application_match_score_controller_show_score(self) -> None:
        expected_response = Response("Score Form", status=200, mimetype="text/html")
        self.match_score_controller.show_score.return_value = expected_response
        builder = EnvironBuilder(path="/match-score", method="GET")
        environ = builder.get_environ()
        response_iterable = self.wrapped_app(environ, self.start_response_mock)
        try:
            response_body = b"".join(response_iterable)
        finally:
            if hasattr(response_iterable, "close"):
                response_iterable.close()

        self.match_score_controller.show_score.assert_called_once()
        called_args, _ = self.match_score_controller.show_score.call_args
        passed_request = called_args[0]
        self.assertIsInstance(passed_request, Request)
        self.assertEqual(passed_request.method, "GET")
        self.assertEqual(passed_request.path, "/match-score")
        self.start_response_mock.assert_called_once()
        status, headers = self.start_response_mock.call_args[0]
        wsgi_headers = Headers(headers)
        content_type = wsgi_headers.get("Content-Type")
        self.assertEqual(status, "200 OK")
        self.assertEqual(content_type, 'text/html; charset=utf-8')
        self.assertEqual(response_body, b"Score Form")

    def test_wsgi_application_match_score_controller_update_score_winner_none(self) -> None:
        expected_response = redirect("/match-score?uuid=123e4567-e89b", code=303)
        self.match_score_controller.update_score.return_value = expected_response
        builder = EnvironBuilder(path="/match-score", method="POST")
        environ = builder.get_environ()
        response_iterable = self.wrapped_app(environ, self.start_response_mock)
        try:
            response_body = b"".join(response_iterable)
        finally:
            if hasattr(response_iterable, "close"):
                response_iterable.close()

        self.match_score_controller.update_score.assert_called_once()
        called_args, _ = self.match_score_controller.update_score.call_args
        passed_request = called_args[0]
        self.assertIsInstance(passed_request, Request)
        self.assertEqual(passed_request.method, "POST")
        self.assertEqual(passed_request.path, "/match-score")
        self.start_response_mock.assert_called_once()
        status, headers = self.start_response_mock.call_args[0]
        wsgi_headers = Headers(headers)
        location = wsgi_headers.get("Location")
        self.assertEqual(status, "303 SEE OTHER")
        self.assertEqual(location, '/match-score?uuid=123e4567-e89b')

    def test_wsgi_application_match_score_controller_update_score_winner_not_none(self) -> None:
        expected_response = Response("Score Form", status=200, mimetype="text/html")
        self.match_score_controller.update_score.return_value = expected_response
        builder = EnvironBuilder(path="/match-score", method="POST")
        environ = builder.get_environ()
        response_iterable = self.wrapped_app(environ, self.start_response_mock)
        try:
            response_body = b"".join(response_iterable)
        finally:
            if hasattr(response_iterable, "close"):
                response_iterable.close()

        self.match_score_controller.update_score.assert_called_once()
        called_args, _ = self.match_score_controller.update_score.call_args
        passed_request = called_args[0]
        self.assertIsInstance(passed_request, Request)
        self.assertEqual(passed_request.method, "POST")
        self.assertEqual(passed_request.path, "/match-score")
        self.start_response_mock.assert_called_once()
        status, headers = self.start_response_mock.call_args[0]
        wsgi_headers = Headers(headers)
        content_type = wsgi_headers.get("Content-Type")
        self.assertEqual(status, "200 OK")
        self.assertEqual(content_type, 'text/html; charset=utf-8')
        self.assertEqual(response_body, b"Score Form")

    def test_wsgi_application_matches_controller_show_finished_matches(self) -> None:
        expected_response = Response("Matches", status=200, mimetype="text/html")
        self.matches_controller.show_finished_matches.return_value = expected_response
        builder = EnvironBuilder(path="/matches", method="GET")
        environ = builder.get_environ()
        response_iterable = self.wrapped_app(environ, self.start_response_mock)
        try:
            response_body = b"".join(response_iterable)
        finally:
            if hasattr(response_iterable, "close"):
                response_iterable.close()

        self.matches_controller.show_finished_matches.assert_called_once()
        called_args, _ = self.matches_controller.show_finished_matches.call_args
        passed_request = called_args[0]
        self.assertIsInstance(passed_request, Request)
        self.assertEqual(passed_request.method, "GET")
        self.assertEqual(passed_request.path, "/matches")
        self.start_response_mock.assert_called_once()
        status, headers = self.start_response_mock.call_args[0]
        wsgi_headers = Headers(headers)
        content_type = wsgi_headers.get("Content-Type")
        self.assertEqual(status, "200 OK")
        self.assertEqual(content_type, 'text/html; charset=utf-8')
        self.assertEqual(response_body, b"Matches")

    def test_wsgi_application_unknown_path(self) -> None:
        builder = EnvironBuilder(path="/unknown", method="GET")
        environ = builder.get_environ()
        response_iterable = self.wrapped_app(environ, self.start_response_mock)
        try:
            response_body = b"".join(response_iterable)
        finally:
            if hasattr(response_iterable, "close"):
                response_iterable.close()

        self.new_match_controller.show_form.assert_not_called()
        self.new_match_controller.create_match.assert_not_called()
        self.match_score_controller.show_score.assert_not_called()
        self.match_score_controller.update_score.assert_not_called()
        self.matches_controller.show_finished_matches.assert_not_called()
        self.start_response_mock.assert_called_once()
        status, headers = self.start_response_mock.call_args[0]
        wsgi_headers = Headers(headers)
        content_type = wsgi_headers.get("Content-Type")
        self.assertEqual(status, "404 NOT FOUND")
        self.assertEqual(content_type, 'text/html')
        self.assertEqual(response_body, b"<h1>404 Not Found</h1>")

    def test_wsgi_application_unknown_method(self) -> None:
        builder = EnvironBuilder(path="/matches", method="PUT")
        environ = builder.get_environ()
        response_iterable = self.wrapped_app(environ, self.start_response_mock)
        try:
            response_body = b"".join(response_iterable)
        finally:
            if hasattr(response_iterable, "close"):
                response_iterable.close()


        self.file_handler.handle.assert_not_called()
        self.new_match_controller.show_form.assert_not_called()
        self.new_match_controller.create_match.assert_not_called()
        self.match_score_controller.show_score.assert_not_called()
        self.match_score_controller.update_score.assert_not_called()
        self.matches_controller.show_finished_matches.assert_not_called()
        self.start_response_mock.assert_called_once()
        status, headers = self.start_response_mock.call_args[0]
        wsgi_headers = Headers(headers)
        content_type = wsgi_headers.get("Content-Type")
        self.assertEqual(status, "405 METHOD NOT ALLOWED")
        self.assertEqual(content_type, "text/html")
        self.assertEqual(response_body, b"<h1>405 Method Not Allowed</h1>")

    def test_wsgi_application_static_path_success(self) -> None:
        builder = EnvironBuilder(path="/static/css/style.css", method="GET")
        environ = builder.get_environ()
        expected_response = Response("body {color: red; }",
                                      status=200,
                                      mimetype="text/css")
        self.file_handler.handle.return_value = expected_response

        response_iterable = self.wrapped_app(environ, self.start_response_mock)
        try:
            response_body = b"".join(response_iterable)
        finally:
            if hasattr(response_iterable, "close"):
                response_iterable.close()

        self.file_handler.handle.assert_called_once_with(environ, "css/style.css")
        self.new_match_controller.show_form.assert_not_called()
        self.new_match_controller.create_match.assert_not_called()
        self.match_score_controller.show_score.assert_not_called()
        self.match_score_controller.update_score.assert_not_called()
        self.matches_controller.show_finished_matches.assert_not_called()
        status, headers = self.start_response_mock.call_args[0]
        wsgi_headers = Headers(headers)
        content_type = wsgi_headers.get("Content-Type")
        self.assertEqual(status, "200 OK")
        self.assertEqual(content_type, 'text/css; charset=utf-8')
        self.assertEqual(response_body, b"body {color: red; }")

    def test_wsgi_application_static_handle_404(self) -> None:
        builder = EnvironBuilder(path="/static/not-found.txt", method="GET")
        environ = builder.get_environ()
        expected_response = Response("<h1>404 File Not Found</h1>",
                                      status=404,
                                      mimetype="text/html")
        self.file_handler.handle.return_value = expected_response

        response_iterable = self.wrapped_app(environ, self.start_response_mock)
        try:
            response_body = b"".join(response_iterable)
        finally:
            if hasattr(response_iterable, "close"):
                response_iterable.close()

        self.file_handler.handle.assert_called_once_with(environ, "not-found.txt")
        self.new_match_controller.show_form.assert_not_called()
        self.new_match_controller.create_match.assert_not_called()
        self.match_score_controller.show_score.assert_not_called()
        self.match_score_controller.update_score.assert_not_called()
        self.matches_controller.show_finished_matches.assert_not_called()
        status, headers = self.start_response_mock.call_args[0]
        wsgi_headers = Headers(headers)
        content_type = wsgi_headers.get("Content-Type")
        self.assertEqual(status, "404 NOT FOUND")
        self.assertEqual(content_type, 'text/html; charset=utf-8')
        self.assertEqual(response_body, b"<h1>404 File Not Found</h1>")

    def test_wsgi_application_static_handle_prohibited_method(self) -> None:
        builder = EnvironBuilder(path="/static/css/style.css", method="POST")
        environ = builder.get_environ()
        response_iterable = self.wrapped_app(environ, self.start_response_mock)
        try:
            response_body = b"".join(response_iterable)
        finally:
            if hasattr(response_iterable, "close"):
                response_iterable.close()

        self.file_handler.handle.assert_not_called()
        self.new_match_controller.show_form.assert_not_called()
        self.new_match_controller.create_match.assert_not_called()
        self.match_score_controller.show_score.assert_not_called()
        self.match_score_controller.update_score.assert_not_called()
        self.matches_controller.show_finished_matches.assert_not_called()
        status, headers = self.start_response_mock.call_args[0]
        wsgi_headers = Headers(headers)
        content_type = wsgi_headers.get("Content-Type")
        allow = wsgi_headers.get("Allow")
        self.assertEqual(allow, "GET, HEAD")
        self.assertEqual(status, "405 METHOD NOT ALLOWED")
        self.assertEqual(content_type, 'text/html')
        self.assertEqual(response_body, b"<h1>405 Method Not Allowed</h1>")

    def test_wsgi_application_static_handle_invalid_routing(self) -> None:
        builder = EnvironBuilder(path="/static", method="GET")
        environ = builder.get_environ()
        response_iterable = self.wrapped_app(environ, self.start_response_mock)
        try:
            response_body = b"".join(response_iterable)
        finally:
            if hasattr(response_iterable, "close"):
                response_iterable.close()

        self.file_handler.handle.assert_not_called()
        self.new_match_controller.show_form.assert_not_called()
        self.new_match_controller.create_match.assert_not_called()
        self.match_score_controller.show_score.assert_not_called()
        self.match_score_controller.update_score.assert_not_called()
        self.matches_controller.show_finished_matches.assert_not_called()
        status, headers = self.start_response_mock.call_args[0]
        wsgi_headers = Headers(headers)
        content_type = wsgi_headers.get("Content-Type")
        self.assertEqual(status, "404 NOT FOUND")
        self.assertEqual(content_type, 'text/html')
        self.assertEqual(response_body, b"<h1>404 Not Found</h1>")

    def test_wsgi_application_static_handle_routing_empty(self) -> None:
        builder = EnvironBuilder(path="/static/", method="GET")
        environ = builder.get_environ()
        expected_response = Response("<h1>404 Not Found</h1>",
                                     status=404,
                                     mimetype="text/html")
        self.file_handler.handle.return_value = expected_response
        response_iterable = self.wrapped_app(environ, self.start_response_mock)
        try:
            response_body = b"".join(response_iterable)
        finally:
            if hasattr(response_iterable, "close"):
                response_iterable.close()

        self.file_handler.handle.assert_called_once_with(environ, "")
        self.new_match_controller.show_form.assert_not_called()
        self.new_match_controller.create_match.assert_not_called()
        self.match_score_controller.show_score.assert_not_called()
        self.match_score_controller.update_score.assert_not_called()
        self.matches_controller.show_finished_matches.assert_not_called()
        status, headers = self.start_response_mock.call_args[0]
        wsgi_headers = Headers(headers)
        content_type = wsgi_headers.get("Content-Type")
        self.assertEqual(status, "404 NOT FOUND")
        self.assertEqual(content_type, 'text/html; charset=utf-8')
        self.assertEqual(response_body, b"<h1>404 Not Found</h1>")







































