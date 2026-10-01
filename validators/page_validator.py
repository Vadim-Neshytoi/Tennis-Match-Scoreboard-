from exceptions.validation_exceptions import InvalidPageError


class PageValidator:
    """Валидатор номера страницы списка завершённых матчей."""

    @staticmethod
    def validate_page(page: str) -> int:
        """Проверяет номер страницы и возвращает его целочисленное значение."""

        try:
            page = int(page)
        except (ValueError, TypeError):
            raise InvalidPageError()
        if page < 1:
            raise InvalidPageError()
        return page
