import re
from exceptions.validation_exceptions import InvalidPlayerNameError


class PlayerNameValidator:
    """Валидатор имени игрока, проверяющий его соответствие установленным правилам."""

    @staticmethod
    def validate_and_normalize_name(name: str, field_name: str) -> str:
        """Проверяет имя игрока и возвращает его нормализованное значение."""

        words = name.split()
        normalized_named = " ".join(words)
        pattern = r'^([A-Za-z]+( [A-Za-z]+)?|[А-Яа-яЁё]+( [А-Яа-яЁё]+)?)$'
        if not 2 <= len(normalized_named) <= 30:
            raise InvalidPlayerNameError(field_name, "Имя должно содержать от 2 до 30 символов")
        if len(words) > 2:
            raise InvalidPlayerNameError(field_name, "Имя может содержать не более двух слов")
        if not re.match(pattern, normalized_named):
            raise InvalidPlayerNameError(field_name, "Используйте только буквы одного алфавита")
        return normalized_named























































































