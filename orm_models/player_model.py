# noinspection PyUnresolvedReferences
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String

from .base import Base


class PlayerModel(Base):
    """ORM-модель игрока для хранения его данных в базе данных."""

    __tablename__ = 'players'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)

    normalized_name: Mapped[str] = mapped_column(String(30), unique=True)

