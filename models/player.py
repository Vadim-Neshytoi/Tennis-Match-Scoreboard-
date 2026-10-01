from exceptions.validation_exceptions import ImmutableAttributeError


class Player:
    """Доменная модель, представляющая игрока теннисного матча."""

    def __init__(self, name: str,  ID: int | None = None) -> None:
        self._id = ID
        self._name = name


    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, ID: int) -> None:
        if self._id is None:
            self._id = ID
        else:
            raise ImmutableAttributeError

    @property
    def name(self) -> str:
        return self._name