from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Self
    from sqlalchemy.orm import Session, sessionmaker

import logging
from mappers.match_mapper import MatchMapper
from mappers.player_mapper import PlayerMapper
from repositories.match_repository import MatchRepository
from repositories.player_repository import PlayerRepository

logger = logging.getLogger(__name__)

class UnitOfWork:
    """Управляет транзакцией и репозиториями в рамках одного сценария работы с базой данных."""

    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._player_repo: PlayerRepository | None = None
        self._match_repo: MatchRepository | None = None
        self._commit_completed: bool = False

    def __enter__(self) -> Self:
        """Создаёт сессию базы данных и репозитории для текущего контекста."""

        self._session = self._session_factory()

        player_mapper = PlayerMapper()
        match_mapper = MatchMapper()
        self._player_repo = PlayerRepository(self._session, player_mapper)
        self._match_repo = MatchRepository(self._session, match_mapper)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Завершает транзакцию и закрывает сессию базы данных."""

        try:
            if exc_type is not None:
                logger.error(f"UOW завершился с ошибкой, выполняем rollback. Ошибка {exc_val}")
                self.rollback()
                return
            elif  self._commit_completed:
                return
            elif self._session.in_transaction():
                logger.warning("Контекст UOW закрывается с активной транзакцией, но метод commit или ручной rollback "
                               "не были вызваны. Выполняем принудительный rollback.")
                self.rollback()
            else:
                pass
        finally:
            self._session.close()

    def commit(self) -> None:
        """Подтверждает транзакцию после успешного выполнения сценария."""

        if self._session is None:
            raise RuntimeError("Нелья вызвать commit() до входа в контекстный менеджер (with)!")
        self._session.commit()
        self._commit_completed = True

    def rollback(self) -> None:
        """Откатывает текущую транзакцию."""

        if self._session and self._session.in_transaction():
            self._session.rollback()

    @property
    def player_repo(self) -> PlayerRepository | None:
        return self._player_repo

    @property
    def match_repo(self) -> MatchRepository | None:
        return self._match_repo













































