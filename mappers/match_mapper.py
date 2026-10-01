from models.match import Match
from orm_models.match_model import MatchModel
from models.player_score import PlayerScore
from.player_mapper import PlayerMapper


class MatchMapper:
    """Маппер преобразует доменную модель матча в ORM-модель и обратно."""

    @staticmethod
    def to_domain(orm_model: MatchModel) -> Match:
        """Преобразует ORM-модель матча в доменную модель."""

        p1_data = orm_model.score.get("player1", {})
        player_1_score = PlayerScore(points=p1_data.get("points"),
                                     games=p1_data.get("games"),
                                     sets=p1_data.get("sets"))
        p2_data = orm_model.score.get("player2", {})
        player_2_score = PlayerScore(points=p2_data.get("points"),
                                     games=p2_data.get("games"),
                                     sets=p2_data.get("sets"))
        domain_player1 = PlayerMapper.to_domain(orm_model.player1)
        domain_player2 = PlayerMapper.to_domain(orm_model.player2)
        winner = PlayerMapper.to_domain(orm_model.winner) if orm_model.winner is not None else None
        return Match(player_1=domain_player1,
                     player_2=domain_player2,
                     player_1_score=player_1_score,
                     player_2_score=player_2_score,
                     uuid=orm_model.uuid,
                     winner=winner
                     )

    @staticmethod
    def to_orm(domain_model: Match) -> MatchModel:
        """Преобразует доменную модель матча в ORM-модель."""

        domain_score_dict = MatchMapper.to_score_dict(domain_model)
        winner = domain_model.winner.id if domain_model.winner is not None else None
        return MatchModel(uuid=domain_model.uuid,
                          player1_id=domain_model.player_1.id,
                          player2_id=domain_model.player_2.id,
                          score=domain_score_dict,
                          winner_id=winner
                          )

    @staticmethod
    def to_score_dict(match: Match) -> dict[str, dict[str, int]]:
        """Преобразует счёт доменной модели матча в структуру данных для хранения."""

        domain_score_dict = {
            "player1": {"points": match.player_1_score.points,
                        "games": match.player_1_score.games,
                        "sets": match.player_1_score.sets},
            "player2": {"points": match.player_2_score.points,
                        "games": match.player_2_score.games,
                        "sets": match.player_2_score.sets},
        }
        return domain_score_dict
































