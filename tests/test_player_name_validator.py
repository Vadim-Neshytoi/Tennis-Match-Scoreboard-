import unittest
from validators.player_name_validator import PlayerNameValidator
from exceptions.validation_exceptions import InvalidPlayerNameError


class TestPlayerRepository(unittest.TestCase):

    def test_player_name_validator(self) -> None:
        field_name = "test_field"
        cases = [
            ("Ия", str),
            ("Alex", str),
            ("Иван", str),
            ("Иван Ванко", str),
            ("ИмяСостоитРовноИзТридцатиБуквЁ", str),
            ("ИмяСостоитБолееЧемИзТридцатиБукв", InvalidPlayerNameError),
            ("AlexИван", InvalidPlayerNameError),
            ("Alex2", InvalidPlayerNameError),
            ("Alex!", InvalidPlayerNameError),
            ("Иван Ван Ко", InvalidPlayerNameError),
            ("Иван Smith", InvalidPlayerNameError),
            ("", InvalidPlayerNameError),
            ("     ", InvalidPlayerNameError),
        ]
        for name, expected_result in cases:
            with self.subTest(f"Проверка для имени {name}"):
                if isinstance(expected_result, type) and issubclass(expected_result, Exception):
                    with self.assertRaises(InvalidPlayerNameError):
                        PlayerNameValidator.validate_and_normalize_name(name=name, field_name=field_name)
                else:
                    validate_name = PlayerNameValidator.validate_and_normalize_name(name=name, field_name=field_name)
                    self.assertIsNotNone(validate_name)
                    self.assertIsInstance(validate_name, expected_result)
                    self.assertEqual(name, validate_name)

    def test_player_name_validator_get_normalized_name(self) -> None:
        field_name = "test_field"
        case = [
            ("  Иван  ", "Иван"),
            ("Иван    Ванко", "Иван Ванко")
        ]
        for name, expected_result in case:
            with self.subTest(f"Проверка для имени {name}"):
                normalized_name = PlayerNameValidator.validate_and_normalize_name(name=name, field_name=field_name)
                self.assertIsNotNone(normalized_name)
                self.assertIsInstance(normalized_name, str)
                self.assertEqual(expected_result, normalized_name)

    def test_player_name_validator_check_field_exception(self) -> None:
        field_name = "player_1"
        name = "Alex!"
        with self.assertRaises(InvalidPlayerNameError) as cm:
            PlayerNameValidator.validate_and_normalize_name(name=name, field_name=field_name)
            exception_obj = cm.exception
            self.assertEqual(exception_obj.field_name, "player_1")
            self.assertEqual(exception_obj.message, "Имя должно состоять исключительно из букв одного \
             алфавита(латиница/кирилица) и не должно содержать цифр и специальных символов")















