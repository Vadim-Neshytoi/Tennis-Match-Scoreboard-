import os
import unittest
from pathlib import Path
from unittest.mock import patch
from settings import Settings
from exceptions.validation_exceptions import ConfigurationError


class TestSettings(unittest.TestCase):

    def setUp(self) -> None:
        test_dir = Path(__file__).resolve().parent
        self.project_root = test_dir.parent

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_url_is_required_otherwise_raises_configuration_error(self) -> None:
        with self.assertRaises(ConfigurationError) as cm:
            Settings.load_from_env()
        self.assertEqual(str(cm.exception), "Ошибка: Переменная окружения DATABASE_URL не задана !")

    @patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://test"})
    def test_settings_static_root_default_resolves_to_project_root_static(self) -> None:
        settings = Settings.load_from_env()
        self.assertEqual(settings.static_root, self.project_root / "static")

    @patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://test"})
    def test_settings_template_dir_default_resolves_to_project_root_templates(self) -> None:
        settings = Settings.load_from_env()
        self.assertEqual(settings.template_dir, self.project_root / "templates")

    @patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://test","STATIC_ROOT": "assets/static"})
    def test_settings_relative_static_root_resolves_relative_to_project_root(self) -> None:
        settings = Settings.load_from_env()
        expected_path = (self.project_root / "assets/static").resolve()
        self.assertEqual(settings.static_root, expected_path)

    @patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://test", "TEMPLATE_DIR": "custom_layouts"})
    def test_settings_relative_template_dir_resolves_relative_to_project_root(self) -> None:
        settings = Settings.load_from_env()
        expected_path = (self.project_root / "custom_layouts").resolve()
        self.assertEqual(settings.template_dir, expected_path)

    @patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://test",
                                    "STATIC_ROOT": "/var/www/static" if os.name != "nt" else "C:\\var\\www\\static"})
    def test_settings_absolute_static_root_remains_absolute(self) -> None:
        settings = Settings.load_from_env()
        raw_env_path = os.environ["STATIC_ROOT"]
        self.assertEqual(settings.static_root, Path(raw_env_path).resolve())

    @patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://test",
                                    "TEMPLATE_DIR": "/var/www/templates" if os.name != "nt" else "C:\\var\\www\\templates"})
    def test_settings_absolute_template_dir_remains_absolute(self) -> None:
        settings = Settings.load_from_env()
        raw_env_path = os.environ["TEMPLATE_DIR"]
        self.assertEqual(settings.template_dir, Path(raw_env_path).resolve())

    @patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://test"})
    def test_settings_host_default_is_four_zeros(self) -> None:
        settings = Settings.load_from_env()
        self.assertEqual(settings.host, "0.0.0.0")

    @patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://test"})
    def test_settings_port_default_is_eight_zero_eight_zero(self) -> None:
        settings = Settings.load_from_env()
        self.assertEqual(settings.port, 8080)

    @patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://test", "PORT": "9000"})
    def test_settings_valid_string_port_is_cast_to_integer(self) -> None:
        settings = Settings.load_from_env()
        self.assertEqual(settings.port, 9000)
        self.assertIsInstance(settings.port, int)

    @patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://test", "PORT": "abc"})
    def test_settings_non_numeric_port_raises_configuration_error(self) -> None:
        with self.assertRaises(ConfigurationError) as cm:
            Settings.load_from_env()
        self.assertIn("Порт должен быть числом", str(cm.exception))

    @patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://test", "PORT": "0"})
    def test_settings_port_zero_is_out_of_bounds_and_raises_configuration_error(self) -> None:
        with self.assertRaises(ConfigurationError) as cm:
            Settings.load_from_env()
        self.assertIn("выходит за допустимый диапазон TCP портов", str(cm.exception))

    @patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://test", "PORT": "65536"})
    def test_settings_port_sixty_five_thousand_five_hundred_thirty_six_raises_configuration_error(self) -> None:
        with self.assertRaises(ConfigurationError) as cm:
            Settings.load_from_env()
        self.assertIn("выходит за допустимый диапазон TCP портов", str(cm.exception))

    @patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://test", "PORT": "1"})
    def test_settings_lower_tcp_boundary_one_is_accepted(self) -> None:
        settings = Settings.load_from_env()
        self.assertEqual(settings.port, 1)

    @patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://test", "PORT": "65535"})
    def test_settings_upper_tcp_boundary_sixty_five_thousand_five_hundred_thirty_five_is_accepted(self) -> None:
        settings = Settings.load_from_env()
        self.assertEqual(settings.port, 65535)



































