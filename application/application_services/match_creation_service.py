from typing import Callable
from exceptions.validation_exceptions import DuplicateNamesAfterNormalizationError
from models.match import Match
from validators.player_name_validator import PlayerNameValidator
from unit_of_work.unit_of_work import UnitOfWork


class MatchCreationService:
    """Сервис создания нового матча с валидацией и сохранением его игроков и состояния."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def create_match(self, player1_name: str, player2_name: str) -> Match:
        """Создаёт и сохраняет новый матч на основе имён двух игроков."""

        normalized_player1_name = PlayerNameValidator.validate_and_normalize_name(player1_name, "player1")
        normalized_player2_name = PlayerNameValidator.validate_and_normalize_name(player2_name, "player2")

        if normalized_player1_name.lower() == normalized_player2_name.lower():
            raise DuplicateNamesAfterNormalizationError("Имена игроков должны различаться")

        with self._uow_factory() as uow:
            domain_player1 = uow.player_repo.find_or_create_player(normalized_player1_name)
            domain_player2 = uow.player_repo.find_or_create_player(normalized_player2_name)
            domain_match = Match(domain_player1, domain_player2)
            uow.match_repo.create_match(domain_match)
            uow.commit()
        return domain_match
















































