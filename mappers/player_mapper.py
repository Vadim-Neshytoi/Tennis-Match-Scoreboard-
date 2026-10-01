from orm_models.player_model import PlayerModel
from models.player import Player


class PlayerMapper:
    """Маппер преобразует доменную модель игрока в ORM-модель и обратно."""

    @staticmethod
    def to_domain(orm_model: PlayerModel) -> Player:
        """Преобразует ORM-модель игрока в доменную модель."""

        return Player(
            ID = orm_model.id,
            name = orm_model.name
        )


    @staticmethod
    def to_orm(domain_model: Player) -> PlayerModel:
        """Преобразует доменную модель игрока в ORM-модель."""

        return PlayerModel(
            id = domain_model.id,
            name = domain_model.name,
            normalized_name = domain_model.name.lower()
        )