from typing import Callable
from exceptions.validation_exceptions import MatchNotFoundError
from models.match import Match
from unit_of_work.unit_of_work import UnitOfWork


class MatchQueryService:
    """Сервис получения доменной модели матча по его UUID."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def get_match_by_uuid(self, uuid: str) -> Match:
        """Возвращает доменную модель матча по его UUID."""

        with self._uow_factory() as uow:
            domain_match = uow.match_repo.find_match_by_uuid(uuid)
            if domain_match is None:
                raise MatchNotFoundError("Матч не найден")
            uow.rollback()
            return domain_match