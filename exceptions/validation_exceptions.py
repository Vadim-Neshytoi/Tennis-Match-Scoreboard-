from .base import ApplicationError

class ImmutableAttributeError(ApplicationError):
    pass

class PlayerNotInMatchError(ApplicationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Ошибка: {self.message}")

class MatchNotInDatabaseError(ApplicationError):
    pass

class MatchNotFoundError(ApplicationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Ошибка: {self.message}")

class InvalidPlayerNameError(ApplicationError):
    def __init__(self, field_name: str, message: str):
        self.field_name = field_name
        self.message = message
        super().__init__(f"Ошибка в поле {field_name} : {self.message}")

class InvalidPageError(ApplicationError):
    def __init__(self):
        super().__init__("Страница должна быть исключительно числом и больше 0")

class PageNotFoundError(ApplicationError):
    def __init__(self):
        super().__init__("Страница не найдена")

class DuplicateNamesAfterNormalizationError(ApplicationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Ошибка: {self.message}")

class ConfigurationError(ApplicationError):
    pass











