from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from validators.player_name_validator import PlayerNameValidator
    from unit_of_work.unit_of_work import UnitOfWork

from exceptions.validation_exceptions import PageNotFoundError
from math import ceil
from typing import Callable
from application.dto.finished_matches_result import FinishedMatchesResult


class FinishedMatchesService:
    """Сервис получения завершённых матчей с поддержкой фильтрации и пагинации."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork], name_validator: PlayerNameValidator,
                 items_per_page: int = 10) -> None:
        self._uow_factory = uow_factory
        self._name_validator = name_validator
        self._items_per_page = items_per_page

    def get_finished_matches(self, page: int, player_name: str | None) -> FinishedMatchesResult:
        """Возвращает страницу завершённых матчей с учётом фильтрации по имени игрока."""

        with self._uow_factory() as uow:
            if player_name is not None:
                normalized_name = self._name_validator.validate_and_normalize_name(name=player_name,
                                                                                   field_name="filter_by_player_name")
                matches, total_count = uow.match_repo.find_finished_matches_page(page=page, page_size=self._items_per_page,
                                                                             player_name=normalized_name)
            else:
                matches, total_count = uow.match_repo.find_finished_matches_page(page=page, page_size=self._items_per_page,
                                                                             player_name=None)

            normalized_player_name = normalized_name if player_name is not None else None
            total_pages = ceil(total_count / self._items_per_page)
            if total_pages == 0:
                result =  FinishedMatchesResult(matches=matches, total_count=total_count, items_per_page=self._items_per_page,
                                             total_pages=total_pages, current_page=1, player_name=normalized_player_name)
            elif page > total_pages:
                raise PageNotFoundError()
            else:
                result =  FinishedMatchesResult(matches=matches, total_count=total_count, items_per_page=self._items_per_page,
                                             total_pages=total_pages, current_page=page, player_name=normalized_player_name)
            uow.rollback()
            return result


































