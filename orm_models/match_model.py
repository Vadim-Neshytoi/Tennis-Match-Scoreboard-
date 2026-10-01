# noinspection PyUnresolvedReferences
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, String, Integer, JSON

from .base import Base


class MatchModel(Base):
    """ORM-модель матча для хранения его состояния и связей в базе данных."""

    __tablename__ = 'matches'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    player1_id: Mapped[int] = mapped_column(Integer, ForeignKey('players.id'), nullable=False)
    player2_id: Mapped[int] = mapped_column(Integer, ForeignKey('players.id'), nullable=False)
    winner_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('players.id'), nullable=True)
    score: Mapped[dict[str, dict[str, int]]] = mapped_column(JSON, nullable=False)

    player1 = relationship("PlayerModel", foreign_keys=[player1_id])
    player2 = relationship("PlayerModel", foreign_keys=[player2_id])
    winner = relationship("PlayerModel", foreign_keys=[winner_id])