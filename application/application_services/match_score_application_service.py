from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.match import Match
    from services.match_score_service import MatchScoreService

from typing import Callable
from unit_of_work.unit_of_work import UnitOfWork
from exceptions.validation_exceptions import MatchNotFoundError


class MatchScoreApplicationService:
    """Сервис изменения счёта матча путём начисления очка выбранному игроку."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork], score_service: MatchScoreService) -> None:
        self._uow_factory = uow_factory
        self._score_service = score_service

    def play_match(self, match_uuid: str, player_id: int) -> Match:
        """Начисляет очко выбранному игроку и возвращает обновлённую доменную модель матча."""

        with self._uow_factory() as uow:
            domain_match = uow.match_repo.find_match_by_uuid(match_uuid)
            if domain_match is None:
                raise MatchNotFoundError("Матч не найден")
            player = domain_match.get_player_by_id(player_id)
            winner = self._score_service.play_match(domain_match, player)
            domain_match.winner = winner
            uow.match_repo.update(domain_match)
            uow.commit()
            return domain_match


















































