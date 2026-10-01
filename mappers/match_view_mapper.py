from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.match import Match
    from services.match_score_service import MatchScoreService

POINT_VALUES = {
    0: "0",
    1: "15",
    2: "30",
    3: "40"
}


class MatchViewMapper:
    """Маппер преобразует доменную модель матча в данные для его отображения."""

    def __init__(self, score_service: MatchScoreService) -> None:
        self._score_service = score_service

    def to_view_data(self, match: Match) -> dict[str, str | None | dict[str, str | int]]:
        """Формирует данные для отображения текущего состояния матча."""

        uuid = match.uuid
        winner_name = match.winner.name if match.winner is not None else None

        name1 = match.player_1.name
        id1 = match.player_1.id
        points1 = match.player_1_score.points
        games1 = match.player_1_score.games
        sets1 = match.player_1_score.sets

        name2 = match.player_2.name
        id2 = match.player_2.id
        points2 = match.player_2_score.points
        games2 = match.player_2_score.games
        sets2 = match.player_2_score.sets

        is_tie_break = self._score_service.is_tie_break(match)

        if is_tie_break:
            points1_display = points1
            points2_display = points2
        else:
            points1_display, points2_display = self.get_display_points(points1, points2)

        return {
            "uuid": uuid,
            "player1": {"name": name1,
                        "id": id1,
                        "points": points1_display,
                        "games": games1,
                        "sets": sets1},
            "player2": {"name": name2,
                        "id": id2,
                        "points": points2_display,
                        "games": games2,
                        "sets": sets2},
            "winner": winner_name
        }

    @staticmethod
    def get_display_points( points1: int, points2: int) -> tuple[str, str]:
        """Возвращает отображаемые значения очков для равного счёта и преимущества."""

        if points1 == points2 and points1 >= 3:
            return "40", "40"
        if points1 >= 4 and points1 - points2 == 1:
            return "AD", "40"
        if points2 >= 4 and points2 - points1 == 1:
            return "40", "AD"
        points1 = POINT_VALUES[points1]
        points2 = POINT_VALUES[points2]
        return points1, points2



























