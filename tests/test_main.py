from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
from settings import Settings
from exceptions.validation_exceptions import ConfigurationError
import main



class TestMainApplicationLifecycle(unittest.TestCase):

    @patch("main.serve")
    @patch("main.create_application")
    @patch.object(Settings, "load_from_env")
    def test_main_with_valid_config_starts_server_successfully(self, mock_load_env, mock_create_app, mock_serve):
        mock_settings = MagicMock()
        mock_settings.db_url = "mysql+pymysql://test"
        mock_settings.static_root = Path("/test/static")
        mock_settings.template_dir = Path("/test/templates")
        mock_settings.host = "127.0.0.1"
        mock_settings.port = 9090
        mock_load_env.return_value = mock_settings

        mock_wsgi_app = MagicMock()
        mock_create_app.return_value = mock_wsgi_app

        main.main()

        mock_create_app.assert_called_once_with(db_url=mock_settings.db_url,
                                                static_root=mock_settings.static_root,
                                                template_dir=mock_settings.template_dir)

        mock_serve.assert_called_once_with(mock_wsgi_app,
                                           host="127.0.0.1",
                                           port=9090)

    @patch("main.sys.stderr")
    @patch("main.serve")
    @patch("main.create_application")
    @patch.object(Settings, "load_from_env")
    def test_main_with_invalid_config_prints_to_stderr_and_exits(self, mock_load_env, mock_create_app, mock_serve,
                                                                 mock_stderr):
        error_text = "Неверный диапазон портов"
        mock_load_env.side_effect = ConfigurationError(error_text)
        with self.assertRaises(SystemExit) as cm:
            main.main()

        self.assertEqual(cm.exception.code, 1)

        mock_stderr_write = mock_stderr.write
        self.assertTrue(mock_stderr_write.called, "Ожидался вывод сообщения об ошибке в stderr")
        combined_stderr_output = "".join(call.args[0] for call in mock_stderr_write.call_args_list)
        self.assertIn("Критическая ошибка запуска", combined_stderr_output)
        self.assertIn(error_text, combined_stderr_output)

        mock_create_app.assert_not_called()
        mock_serve.assert_not_called()