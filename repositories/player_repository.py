from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mappers.player_mapper import PlayerMapper
    from sqlalchemy.orm import Session

from models.player import Player
from orm_models.player_model import PlayerModel


class PlayerRepository:
    """Репозиторий для сохранения и получения доменных моделей игроков из базы данных."""

    def __init__(self, db_session: Session, mapper: PlayerMapper) -> None:
        self._session = db_session
        self._player_mapper = mapper

    def find_player_by_name(self, name: str) -> Player | None:
        """Возвращает доменнуюую модель игрока по имени или None, если игрок не найден."""

        player_model = self._session.query(PlayerModel).filter(PlayerModel.normalized_name == name.lower()).first()
        if player_model is None:
            return None
        return self._player_mapper.to_domain(player_model)


    def save(self, player: Player) -> Player:
        """Сохраняет нового игрока в базе данных и возвращает его доменную модель."""

        player_model = self._player_mapper.to_orm(player)
        self._session.add(player_model)
        self._session.flush()
        player.id = player_model.id
        return player

    def find_or_create_player(self, normalized_name: str) -> Player:
        """Возвращает существующего игрока по имени или создаёт нового, если игрок не найден."""

        player_domain = self.find_player_by_name(normalized_name)
        if player_domain is None:
            player = Player(normalized_name)
            player_domain = self.save(player)
            return player_domain
        else:
            return player_domain




























