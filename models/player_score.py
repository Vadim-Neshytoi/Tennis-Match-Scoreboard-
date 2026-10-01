from dataclasses import dataclass


@dataclass
class PlayerScore:
    """Доменная модель, представляющая текущий счёт игрока в матче."""

    points: int = 0
    games: int = 0
    sets: int = 0