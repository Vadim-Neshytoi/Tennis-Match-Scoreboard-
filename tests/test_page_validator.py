import unittest
from validators.page_validator import PageValidator
from exceptions.validation_exceptions import InvalidPageError


class TestPageValidator(unittest.TestCase):

    def test_page_validator(self) -> None:
        cases = [
            ("1", 1),
            ("5", 5),
            ("05", 5),
            ("+5", 5),
            (" 5 ", 5),
            ("0", InvalidPageError),
            ("-1", InvalidPageError),
            ("abc", InvalidPageError),
            ("1.5", InvalidPageError),
            ("", InvalidPageError)
        ]
        for value, expected_result in cases:
            with self.subTest(f"Проверка для значения {value} ожидаемое значение {expected_result}"):
                if isinstance(expected_result, type) and issubclass(expected_result, Exception):
                    with self.assertRaises(expected_result):
                        PageValidator.validate_page(value)
                else:
                    result = PageValidator.validate_page(value)

                    self.assertIsNotNone(result)
                    self.assertEqual(result, expected_result)
                    self.assertIsInstance(result, int)
