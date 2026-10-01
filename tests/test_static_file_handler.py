import unittest
import tempfile
from pathlib import Path
from werkzeug.test import EnvironBuilder # noqa
from wsgi_application.static_file_handler import StaticFileHandler


class TestStaticFileHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.switch_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.switch_dir.name)

        self.static_root = self.tmp_path / "static"
        self.static_root.mkdir()

        self.css_dir = self.static_root / "css"
        self.css_dir.mkdir()
        self.style_file = self.css_dir / "style.css"
        self.style_file.write_text("body {color: red; }", encoding="utf-8")

        self.secret_file = self.tmp_path / "secret.txt"
        self.secret_file.write_text("password123", encoding="utf-8")
        self.handler = StaticFileHandler(static_root=self.static_root)

    def tearDown(self) -> None:
        self.switch_dir.cleanup()

    def test_static_file_handler_success(self) -> None:
        builder = EnvironBuilder(path="/static/css/style.css", method="GET")
        environ = builder.get_environ()
        relative_path = "css/style.css"

        response = self.handler.handle(environ, relative_path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/css")

        with response:
            body = b"".join(response.get_app_iter(environ))
            self.assertIn(b"body {color: red; }", body)

    def test_static_file_handler_file_not_found(self) -> None:
        builder = EnvironBuilder(path="/static/not-found.txt", method="GET")
        environ = builder.get_environ()
        relative_path = "not-found.txt"

        response = self.handler.handle(environ, relative_path)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "text/html")

    def test_static_file_handler_unsafe_path(self) -> None:
        builder = EnvironBuilder(path="/static/css/../../secret.txt", method="GET")
        environ = builder.get_environ()
        relative_path = "css/../../secret.txt"

        response = self.handler.handle(environ, relative_path)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "text/html")

    def test_static_file_handler_unknown_mime_type(self) -> None:
        unknown_file = self.static_root / "data_file.unknown"
        unknown_file.write_text("some binary data", encoding="utf-8")

        builder = EnvironBuilder(path="/static/data_file.unknown", method="GET")
        environ = builder.get_environ()
        relative_path = "data_file.unknown"

        response = self.handler.handle(environ, relative_path)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/octet-stream")

        with response:
            body = b"".join(response.get_app_iter(environ))
            self.assertIn(b"some binary data", body)

    def test_static_file_handler_directory_not_file(self) -> None:
        builder = EnvironBuilder(path="/static/css", method="GET")
        environ = builder.get_environ()
        relative_path = "css"

        response = self.handler.handle(environ, relative_path)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "text/html")
























