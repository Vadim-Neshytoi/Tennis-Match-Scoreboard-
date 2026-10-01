from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application.dto.finished_matches_result import FinishedMatchesResult

from urllib.parse import urlencode


class FinishedMatchViewMapper:
    """Маппер преобразует результат получения завершённых матчей в данные для представления."""

    @staticmethod
    def _build_pagination_url(page: int, player_name: str | None) -> str:
        """Формирует URL для перехода между страницами списка завершённых матчей."""

        params: dict[str, int | str] = {"page": page}
        if player_name:
            params["filter_by_player_name"] = player_name
        return f"/matches?{urlencode(params)}"

    def to_view_data(self, finished_matches_result: FinishedMatchesResult) -> dict:
        """Формирует данные для представления страницы завершённых матчей."""

        total_count = finished_matches_result.total_count
        items_per_page = finished_matches_result.items_per_page
        current_page = finished_matches_result.current_page
        total_pages = finished_matches_result.total_pages
        player_name = finished_matches_result.player_name
        result = {
            "matches": [],
            "total_count": total_count,
            "items_per_page": items_per_page,
            "current_page": current_page,
            "total_pages": total_pages,
            "pagination": {
                "previous_url": (
                    self._build_pagination_url(current_page - 1, player_name) if current_page > 1 else None
                ),
                "pages": [
                    {
                        "number": page,
                        "url": self._build_pagination_url(page, player_name),
                    }
                    for page in range(1, total_pages + 1)
                ],
                "next_url": (
                    self._build_pagination_url(current_page + 1, player_name) if current_page < total_pages else None
                ),
            },
        }
        for match in finished_matches_result.matches:
            player1 = match.player_1.name
            player2 = match.player_2.name
            winner = match.winner.name
            match_data = {
                "player1": player1,
                "player2": player2,
                "winner": winner,
            }
            result["matches"].append(match_data)
        return result














