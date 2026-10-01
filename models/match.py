import uuid
from dataclasses import dataclass, field
from .player import Player
from .player_score import PlayerScore
from exceptions.validation_exceptions import PlayerNotInMatchError


@dataclass
class Match:
    """Доменная модель, представляющая состояние теннисного матча."""

    player_1: Player
    player_2: Player
    player_1_score: PlayerScore = field(default_factory=PlayerScore)
    player_2_score: PlayerScore = field(default_factory=PlayerScore)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    winner: Player | None = None


    def get_player_by_id(self, player_id: int) -> Player:
        """Возвращает игрока матча по его идентификатору."""

        if player_id == self.player_1.id:
            return self.player_1
        elif player_id == self.player_2.id:
            return self.player_2
        else:
            raise PlayerNotInMatchError("Данный игрок в этом матче не учавствует")
