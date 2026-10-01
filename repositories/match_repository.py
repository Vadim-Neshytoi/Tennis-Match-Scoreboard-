from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.match import Match
    from mappers.match_mapper import MatchMapper

from sqlalchemy import select, func, or_
from sqlalchemy.orm import joinedload, Session, aliased
from exceptions.validation_exceptions import MatchNotInDatabaseError
from orm_models.player_model import PlayerModel
from orm_models.match_model import MatchModel


class MatchRepository:
    """Репозиторий для сохранения и получения доменных моделей матчей из базы данных."""

    def __init__(self, db_session: Session, mapper: MatchMapper) -> None:
        self._session = db_session
        self._match_mapper = mapper

    def find_match_by_uuid(self, uuid: str) -> Match | None:
        """Возвращает доменную модель матча по его UUID или None, если матч не найден."""

        db_orm_match = (self._session.query(MatchModel).options(joinedload(MatchModel.player1),
                                                                     joinedload(MatchModel.player2))
                                                                    .filter(MatchModel.uuid == uuid).first())
        if db_orm_match is None:
            return None
        return self._match_mapper.to_domain(db_orm_match)

    def find_finished_matches_page(self, page: int, page_size: int, player_name: str | None) -> tuple[list[Match], int]:
        """Возвращает страницу завершённых матчей и общее количество найденных матчей."""

        statement = (select(MatchModel).where(MatchModel.winner_id.is_not(None)))

        count_statement = (select(func.count(MatchModel.id)).where(MatchModel.winner_id.is_not(None)))
        if player_name:
            normalized_name = player_name.lower()
            p1_alias = aliased(PlayerModel, name="player1") # alias — это временное отдельное имя, под которым сущность используется
            p2_alias = aliased(PlayerModel, name="player2") # внутри конкретного запроса, чтобы отличить одну её роль от другой.
            name_filter = or_(p1_alias.normalized_name == normalized_name,
                              p2_alias.normalized_name == normalized_name)
            statement = (statement.join(MatchModel.player1.of_type(p1_alias))
                                  .join(MatchModel.player2.of_type(p2_alias)).where(name_filter))
            count_statement = (count_statement.join(MatchModel.player1.of_type(p1_alias))
                                              .join(MatchModel.player2.of_type(p2_alias)).where(name_filter))

        total_count = self._session.execute(count_statement).scalar()
        offset_value = (page - 1) * page_size
        statement = (statement.order_by(MatchModel.id.desc()).limit(page_size).offset(offset_value)
                     .options(joinedload(MatchModel.player1),
                              joinedload(MatchModel.player2)))
        result = self._session.execute(statement)
        orm_matches = result.scalars().all()
        domain_matches = [self._match_mapper.to_domain(orm) for orm in orm_matches]
        return domain_matches, total_count


    def create_match(self, match: Match) -> None:
        """Сохраняет новый матч в базе данных."""

        match_model = self._match_mapper.to_orm(match)
        self._session.add(match_model)
        self._session.flush()

    def update(self, match: Match) -> None:
        """Обновляет существующий матч в базе данных."""

        db_orm_match = self._session.query(MatchModel).filter(MatchModel.uuid == match.uuid).first()
        if db_orm_match is None:
            raise MatchNotInDatabaseError()
        new_score = self._match_mapper.to_score_dict(match)
        db_orm_match.score = new_score
        winner = match.winner
        if winner is None:
            db_orm_match.winner_id = None
        else:
            db_orm_match.winner_id = winner.id
        self._session.flush()
























