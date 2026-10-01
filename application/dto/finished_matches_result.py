from dataclasses import dataclass
from models.match import Match


@dataclass(slots=True, frozen=True)
class FinishedMatchesResult:
    """Контейнер данных, представляющий результат use case получения страницы завершённых матчей и
     предназначенный для передачи из прикладного слоя в Controller."""

    matches: list[Match]
    total_count: int
    items_per_page: int
    total_pages: int
    current_page: int
    player_name: str | None
































