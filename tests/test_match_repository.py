import unittest
import uuid
from dataclasses import asdict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.match import Match
from models.player import Player
from models.player_score import PlayerScore
from orm_models.base import Base
from orm_models.player_model import PlayerModel
from orm_models.match_model import MatchModel
from repositories.match_repository import MatchRepository
from mappers.match_mapper import MatchMapper
from exceptions.validation_exceptions import MatchNotInDatabaseError


class TestMatchRepository(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """Специальный метод unittest, который выполняется один раз перед всеми тестами класса."""
        cls.engine = create_engine(
            'sqlite:///:memory:')  # Engine—это объект,через который SQLAlchemy получает доступ к базе данных
        Base.metadata.create_all(
            cls.engine)  # Base.metadata содержит описание всех зарегистрированных SQLAlchemy-моделей
        cls.SessionFactory = sessionmaker()  # Здесь создаётся фабрика Session, а не сама Session.

    @classmethod
    def tearDownClass(cls) -> None:
        """Аналог setUpClass(), только выполняется один раз после всех тестов."""
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose()

    def setUp(self) -> None:
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()

        self.session = self.SessionFactory(bind=self.connection)
        self.repository = MatchRepository(self.session, MatchMapper())

    def tearDown(self) -> None:
        self.session.close()
        self.transaction.rollback()
        self.connection.close()

    def add_test_db_players(self, id1: int, id2: int, name1: str = "Alex", name2: str = "Bob") -> tuple[PlayerModel, PlayerModel]:
        test_db_player_1 = PlayerModel(id=id1, name=name1, normalized_name=name1.lower())
        test_db_player_2 = PlayerModel(id=id2, name=name2, normalized_name=name2.lower())
        self.session.add(test_db_player_1)
        self.session.add(test_db_player_2)
        self.session.flush()
        return test_db_player_1, test_db_player_2

    def add_test_match_model(self, match_uuid: str, player_1_id: int, player_2_id: int,
                             winner_id: int | None, score_dict: dict[str, dict[str, int]]) -> None:
        orm_match_model = MatchModel(uuid=match_uuid, player1_id=player_1_id, player2_id=player_2_id,
                                     winner_id=winner_id, score=score_dict)
        self.session.add(orm_match_model)
        self.session.flush()

    @staticmethod
    def create_domain_match(test_db_player_1: PlayerModel, test_db_player_2: PlayerModel,
                            p1_score: PlayerScore | None = None, p2_score: PlayerScore | None = None,
                            winner: Player | None = None) -> Match:
        player_1 = Player(name=test_db_player_1.name, ID=test_db_player_1.id)
        player_2 = Player(name=test_db_player_2.name, ID=test_db_player_2.id)
        player_1_score = p1_score if p1_score is not None else PlayerScore(0, 0, 0)
        player_2_score = p2_score if p2_score is not None else PlayerScore(0, 0, 0)
        domain_match = Match(player_1=player_1, player_2=player_2,
                             player_1_score=player_1_score, player_2_score=player_2_score, winner=winner)
        return domain_match

    def add_match_with_existing_players_in_db(self, test_db_player_1: PlayerModel, test_db_player_2: PlayerModel,
                                              player_1_score: PlayerScore, player_2_score: PlayerScore,
                                              winner: Player | None = None) -> Match:
        domain_match = self.create_domain_match(test_db_player_1, test_db_player_2, player_1_score,
                                                player_2_score, winner)
        actual_score_dict = {"player1": asdict(domain_match.player_1_score),
                             "player2": asdict(domain_match.player_2_score)}

        self.add_test_match_model(domain_match.uuid, domain_match.player_1.id, domain_match.player_2.id,
                                  domain_match.winner.id if winner is not None else None, actual_score_dict)
        return domain_match

    def add_player_and_match_in_db(self, id1: int, id2: int, name1: str, name2: str, p1_score: PlayerScore | None = None,
                                   p2_score: PlayerScore | None = None, winner: Player | None = None) -> Match:
        test_db_player_1, test_db_player_2 = self.add_test_db_players(id1, id2, name1, name2)
        player_1_score = p1_score if p1_score is not None else PlayerScore(0, 0, 0)
        player_2_score = p2_score if p2_score is not None else PlayerScore(0, 0, 0)
        domain_match = self.add_match_with_existing_players_in_db(test_db_player_1, test_db_player_2, player_1_score,
                                                                  player_2_score, winner)
        return domain_match

    def test_create_match(self) -> None:
        test_db_player_1, test_db_player_2 = self.add_test_db_players(1, 2)
        new_match = self.create_domain_match(test_db_player_1, test_db_player_2)
        expected_uuid = new_match.uuid

        actual_score_dict = {"player1": asdict(new_match.player_1_score), "player2": asdict(new_match.player_2_score)}
        result = self.repository.create_match(new_match)
        orm_match_model = (self.session.query(MatchModel).filter(MatchModel.uuid == expected_uuid).first())


        self.assertIsNone(result)
        self.assertIsNotNone(orm_match_model)
        self.assertEqual(orm_match_model.uuid, expected_uuid)
        self.assertEqual(orm_match_model.player1_id, new_match.player_1.id)
        self.assertEqual(orm_match_model.player2_id, new_match.player_2.id)
        self.assertIsNone(orm_match_model.winner_id)
        self.assertEqual(orm_match_model.score, actual_score_dict)

    def test_find_match_by_uuid(self) -> None:
        test_db_player_1, test_db_player_2 = self.add_test_db_players(1, 2)
        domain_match = self.create_domain_match(test_db_player_1, test_db_player_2)
        domain_match.winner = domain_match.player_2
        actual_score_dict = {"player1": asdict(domain_match.player_1_score),
                             "player2": asdict(domain_match.player_2_score)}
        orm_match_model = MatchModel(uuid=domain_match.uuid, player1_id=domain_match.player_1.id,
                                     player2_id=domain_match.player_2.id, winner_id=domain_match.winner.id, score=actual_score_dict)
        self.session.add(orm_match_model)
        self.session.flush()

        result = self.repository.find_match_by_uuid(domain_match.uuid)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.winner)
        self.assertEqual(orm_match_model.uuid, result.uuid)
        self.assertEqual(orm_match_model.player1_id, result.player_1.id)
        self.assertEqual(orm_match_model.player1.name, result.player_1.name)
        self.assertEqual(orm_match_model.player2_id, result.player_2.id)
        self.assertEqual(orm_match_model.player2.name, result.player_2.name)
        self.assertEqual(domain_match.winner.id, result.winner.id)
        self.assertEqual(domain_match.winner.name, result.winner.name)
        self.assertEqual(orm_match_model.score["player1"], asdict(result.player_1_score))
        self.assertEqual(orm_match_model.score["player2"], asdict(result.player_2_score))

    def test_find_match_by_uuid_none(self) -> None:
        self.add_player_and_match_in_db(1, 2, "Alex", "Bob")
        unknown_uuid = str(uuid.uuid4())

        result = self.repository.find_match_by_uuid(unknown_uuid)

        self.assertIsNone(result)

    def test_update_match(self) -> None:
        test_db_player_1, test_db_player_2 = self.add_test_db_players(1, 2,)
        domain_match = self.create_domain_match(test_db_player_1, test_db_player_2,)
        actual_score_dict = {"player1": asdict(domain_match.player_1_score),
                            "player2": asdict(domain_match.player_2_score)}
        self.add_test_match_model(domain_match.uuid, domain_match.player_1.id, domain_match.player_2.id,
                                  None, actual_score_dict)
        domain_match.player_1_score.points = 1
        new_actual_score_dict = {"player1": asdict(domain_match.player_1_score),
                            "player2": asdict(domain_match.player_2_score)}

        count_before_update = self.session.query(MatchModel).count()
        result = self.repository.update(domain_match)
        count_after_update = self.session.query(MatchModel).count()
        orm_match_model = (self.session.query(MatchModel).filter(MatchModel.uuid == domain_match.uuid).first())


        self.assertIsNone(result)
        self.assertEqual(orm_match_model.score, new_actual_score_dict)
        self.assertIsNone(orm_match_model.winner_id)
        self.assertEqual(count_before_update, count_after_update)

    def test_update_match_with_winner(self) -> None:
        player_1_score = PlayerScore(0, 0, 1)
        player_2_score = PlayerScore(0, 0, 1)
        player_1 = Player("Alex", 1)
        domain_match = self.add_player_and_match_in_db(1, 2, "Alex", "Bob", player_1_score, player_2_score)


        domain_match.player_1_score.sets = 2
        new_actual_score_dict = {"player1": asdict(domain_match.player_1_score),
                                 "player2": asdict(domain_match.player_2_score)}
        domain_match.winner = domain_match.player_1
        result = self.repository.update(domain_match)
        orm_match_model = (self.session.query(MatchModel).filter(MatchModel.uuid == domain_match.uuid).first())

        self.assertIsNone(result)
        self.assertEqual(orm_match_model.score, new_actual_score_dict)
        self.assertIsNotNone(orm_match_model.winner_id)
        self.assertEqual(orm_match_model.winner_id, domain_match.player_1.id)

    def test_update_match_not_in_database_raises_error(self) -> None:
        player_1_score = PlayerScore(3, 6, 1)
        player_2_score = PlayerScore(1, 2, 1)
        self.add_player_and_match_in_db(1, 2,"Alex", "Bob", player_1_score, player_2_score)
        test_2_db_player_1, test_2_db_player_2 = self.add_test_db_players(3, 4, "Din", "Don")
        domain_match_2 = self.create_domain_match(test_2_db_player_1, test_2_db_player_2)


        with self.assertRaises(MatchNotInDatabaseError):
            self.repository.update(domain_match_2)

    def test_find_finished_matches_page_returns_empty_when_no_finished_matches(self) -> None:
        self.add_player_and_match_in_db(1, 2,"Alex", "Bob")
        expected_result = ([], 0)

        real_result = self.repository.find_finished_matches_page(1, 3, None)

        self.assertEqual(real_result, expected_result)

    def test_find_finished_matches_page(self) -> None:
        self.add_player_and_match_in_db(3, 4,"Alex", "Bob")
        winner_1 = Player("Don", 2)
        winner_2 = Player("Duck", 5)

        player_1_score_1 = PlayerScore(0, 0, 1)
        player_2_score_1 = PlayerScore(0, 0, 2)
        domain_match_2 = self.add_player_and_match_in_db(1, 2,"Din", "Don",
                                                         player_1_score_1, player_2_score_1, winner_2)

        player_1_score_2 = PlayerScore(0, 0, 1)
        player_2_score_2 = PlayerScore(0, 0, 2)
        domain_match_3 = self.add_player_and_match_in_db(5, 6,"Duck", "Dil",
                                                         player_1_score_2, player_2_score_2, winner_1)
        expected_uuids = [domain_match_2.uuid, domain_match_3.uuid]


        result = self.repository.find_finished_matches_page(1, 2, None)
        list_matches, total_count = result
        all_returned_uuids = [domain_match.uuid for domain_match in list_matches]


        self.assertEqual(total_count, 2)
        self.assertEqual(len(list_matches), 2)
        self.assertEqual(set(all_returned_uuids), set(expected_uuids))

    def test_find_finished_matches_page_1(self) -> None:
        player_1_score_1 = PlayerScore(0, 0, 1)
        player_2_score_1 = PlayerScore(0, 0, 2)
        winner = Player("Bob", 2)
        domain_match_1 = self.add_player_and_match_in_db(1, 2,"Alex", "Bob",
                                                         player_1_score_1, player_2_score_1, winner)

        player_1_score_2 = PlayerScore(0, 0, 1)
        player_2_score_2 = PlayerScore(0, 0, 2)
        winner = Player("Don", 4)
        domain_match_2 = self.add_player_and_match_in_db(3, 4,"Din", "Don",
                                                         player_1_score_2, player_2_score_2, winner)

        player_1_score_3 = PlayerScore(0, 0, 2)
        player_2_score_3 = PlayerScore(0, 0, 1)
        winner = Player("Dan", 5)
        domain_match_3 = self.add_player_and_match_in_db(5, 6,"Dan", "Duck",
                                                         player_1_score_3, player_2_score_3, winner)

        player_1_score_4 = PlayerScore(0, 0, 1)
        player_2_score_4 = PlayerScore(0, 0, 2)
        winner = Player("Dil", 8)
        domain_match_4 = self.add_player_and_match_in_db(7, 8,"Dock", "Dil",
                                                         player_1_score_4, player_2_score_4, winner)

        player_1_score_5 = PlayerScore(0, 0, 2)
        player_2_score_5 = PlayerScore(0, 0, 1)
        winner = Player("Lex", 9)
        domain_match_5 = self.add_player_and_match_in_db(9, 10,"Lex", "Lack",
                                                         player_1_score_5, player_2_score_5, winner)

        result = self.repository.find_finished_matches_page(1, 2, None)
        list_matches, total_count = result

        self.assertEqual(total_count, 5)
        self.assertEqual(len(list_matches), 2)
        self.assertEqual(list_matches[0].uuid, domain_match_5.uuid)
        self.assertEqual(list_matches[1].uuid, domain_match_4.uuid)

    def test_find_finished_matches_page_2(self) -> None:
        player_1_score_1 = PlayerScore(0, 0, 1)
        player_2_score_1 = PlayerScore(0, 0, 2)
        winner = Player("Bob", 2)
        domain_match_1 = self.add_player_and_match_in_db(1, 2,"Alex", "Bob",
                                                         player_1_score_1, player_2_score_1, winner)

        player_1_score_2 = PlayerScore(0, 0, 1)
        player_2_score_2 = PlayerScore(0, 0, 2)
        winner = Player("Don", 4)
        domain_match_2 = self.add_player_and_match_in_db(3, 4,"Din", "Don",
                                                         player_1_score_2, player_2_score_2, winner)

        player_1_score_3 = PlayerScore(0, 0, 2)
        player_2_score_3 = PlayerScore(0, 0, 1)
        winner = Player("Dil", 5)
        domain_match_3 = self.add_player_and_match_in_db(5, 6,"Dan", "Duck",
                                                         player_1_score_3, player_2_score_3, winner)

        player_1_score_4 = PlayerScore(0, 0, 1)
        player_2_score_4 = PlayerScore(0, 0, 2)
        winner = Player("Lex", 8)
        domain_match_4 = self.add_player_and_match_in_db(7, 8,"Dock", "Dil",
                                                         player_1_score_4, player_2_score_4, winner)

        player_1_score_5 = PlayerScore(0, 0, 2)
        player_2_score_5 = PlayerScore(0, 0, 1)
        winner = Player("Lex", 9)
        domain_match_5 = self.add_player_and_match_in_db(9, 10,"Lex", "Lack",
                                                         player_1_score_5, player_2_score_5, winner)

        result = self.repository.find_finished_matches_page(2, 2, None)
        list_matches, total_count = result

        self.assertEqual(total_count, 5)
        self.assertEqual(len(list_matches), 2)
        self.assertEqual(list_matches[0].uuid, domain_match_3.uuid)
        self.assertEqual(list_matches[1].uuid, domain_match_2.uuid)

    def test_find_finished_matches_page_3(self) -> None:
        player_1_score_1 = PlayerScore(0, 0, 1)
        player_2_score_1 = PlayerScore(0, 0, 2)
        winner = Player("Bob", 2)
        domain_match_1 = self.add_player_and_match_in_db(1, 2, "Alex", "Bob",
                                                         player_1_score_1, player_2_score_1, winner)

        player_1_score_2 = PlayerScore(0, 0, 1)
        player_2_score_2 = PlayerScore(0, 0, 2)
        winner = Player("Don", 4)
        domain_match_2 = self.add_player_and_match_in_db(3, 4, "Din", "Don",
                                                         player_1_score_2, player_2_score_2, winner)

        player_1_score_3 = PlayerScore(0, 0, 2)
        player_2_score_3 = PlayerScore(0, 0, 1)
        winner = Player("Dan", 5)
        domain_match_3 = self.add_player_and_match_in_db(5, 6, "Dan", "Duck",
                                                         player_1_score_3, player_2_score_3, winner)

        player_1_score_4 = PlayerScore(0, 0, 1)
        player_2_score_4 = PlayerScore(0, 0, 2)
        winner = Player("Dil", 8)
        domain_match_4 = self.add_player_and_match_in_db(7, 8, "Dock", "Dil",
                                                         player_1_score_4, player_2_score_4, winner)

        player_1_score_5 = PlayerScore(0, 0, 2)
        player_2_score_5 = PlayerScore(0, 0, 1)
        winner = Player("Lex", 9)
        domain_match_5 = self.add_player_and_match_in_db(9, 10, "Lex", "Lack",
                                                         player_1_score_5, player_2_score_5, winner)

        result = self.repository.find_finished_matches_page(3, 2, None)
        list_matches, total_count = result

        self.assertEqual(total_count, 5)
        self.assertEqual(len(list_matches), 1)
        self.assertEqual(list_matches[0].uuid, domain_match_1.uuid)

    def test_find_finished_matches_page_by_name(self) -> None:
        test_db_player_1, test_db_player_2 = self.add_test_db_players(1, 2,"Alex", "Bob")
        test_db_player_3, test_db_player_4 = self.add_test_db_players(3, 4, "Din", "Don")
        player_1_score_1 = PlayerScore(0, 0, 1)
        player_2_score_1 = PlayerScore(0, 0, 2)
        player_2 = Player("Bob", 2)
        player_1 = Player("Alex", 1)

        domain_match_1 = self.add_match_with_existing_players_in_db(test_db_player_1, test_db_player_2, player_1_score_1,
                                                                    player_2_score_1, player_2)

        player_1_score_2 = PlayerScore(0, 0, 2)
        player_2_score_2 = PlayerScore(0, 0, 1)
        domain_match_2 = self.add_match_with_existing_players_in_db(test_db_player_1, test_db_player_3, player_1_score_2,
                                                                    player_2_score_2, player_1)

        player_1_score_3 = PlayerScore(0, 0, 2)
        player_2_score_3 = PlayerScore(0, 0, 1)
        domain_match_3 = self.add_match_with_existing_players_in_db(test_db_player_2, test_db_player_4, player_1_score_3,
                                                                    player_2_score_3, player_2)

        result = self.repository.find_finished_matches_page(1, 10, "Bob")
        list_matches, total_count = result

        self.assertEqual(total_count, 2)
        self.assertEqual(len(list_matches), 2)
        self.assertEqual(list_matches[0].uuid, domain_match_3.uuid)
        self.assertEqual(list_matches[1].uuid, domain_match_1.uuid)

    def test_find_finished_matches_page_by_unknown_name(self) -> None:
        test_db_player_1, test_db_player_2 = self.add_test_db_players(1, 2, "Alex", "Bob")
        test_db_player_3, test_db_player_4 = self.add_test_db_players(3, 4, "Din", "Don")
        player_1_score_1 = PlayerScore(0, 0, 1)
        player_2_score_1 = PlayerScore(0, 0, 2)
        player_2 = Player("Bob", 2)
        domain_match_1 = self.add_match_with_existing_players_in_db(test_db_player_1, test_db_player_2, player_1_score_1,
                                                                    player_2_score_1, player_2)

        player_1_score_2 = PlayerScore(0, 0, 2)
        player_2_score_2 = PlayerScore(0, 0, 1)
        player_1 = Player("Alex", 1)
        domain_match_2 = self.add_match_with_existing_players_in_db(test_db_player_3, test_db_player_4, player_1_score_2,
                                                                    player_2_score_2, player_1)

        result = self.repository.find_finished_matches_page(1, 10, "Mick")
        expected_result = ([], 0)

        self.assertEqual(result,expected_result)

    def test_find_finished_matches_page_by_name_pagination(self) -> None:
        test_db_player_1, test_db_player_2 = self.add_test_db_players(1, 2, "Alex", "Bob")
        test_db_player_3, test_db_player_4 = self.add_test_db_players(3, 4, "Din", "Don")
        player_1_score_1 = PlayerScore(0, 0, 1)
        player_2_score_1 = PlayerScore(0, 0, 2)
        player_1 = Player("Alex", 1)
        player_2 = Player("Bob", 2)
        player_3 = Player("Din", 3)
        player_4 = Player("Don", 4)

        domain_match_1 = self.add_match_with_existing_players_in_db(test_db_player_1, test_db_player_2, player_1_score_1,
                                                                    player_2_score_1, player_2)

        player_1_score_2 = PlayerScore(0, 0, 2)
        player_2_score_2 = PlayerScore(0, 0, 1)
        domain_match_2 = self.add_match_with_existing_players_in_db(test_db_player_1, test_db_player_3, player_1_score_2,
                                                                    player_2_score_2, player_3)

        player_1_score_3 = PlayerScore(0, 0, 2)
        player_2_score_3 = PlayerScore(0, 0, 1)
        domain_match_3 = self.add_match_with_existing_players_in_db(test_db_player_2, test_db_player_4, player_1_score_3,
                                                                    player_2_score_3, player_2)

        player_1_score_4 = PlayerScore(0, 0, 1)
        player_2_score_4 = PlayerScore(0, 0, 2)
        domain_match_4 = self.add_match_with_existing_players_in_db(test_db_player_3, test_db_player_4, player_1_score_4,
                                                                    player_2_score_4, player_1)

        player_1_score_5 = PlayerScore(0, 0, 1)
        player_2_score_5 = PlayerScore(0, 0, 2)
        domain_match_5 = self.add_match_with_existing_players_in_db(test_db_player_2, test_db_player_3, player_1_score_5,
                                                                    player_2_score_5, player_3)


        result = self.repository.find_finished_matches_page(1, 2, "dIn")
        list_matches, total_count = result

        result_2 = self.repository.find_finished_matches_page(2, 2, "diN")
        list_matches_2, total_count_2 = result_2

        self.assertEqual(total_count, 3)
        self.assertEqual(len(list_matches), 2)
        self.assertEqual(list_matches[0].uuid, domain_match_5.uuid)
        self.assertEqual(list_matches[1].uuid, domain_match_4.uuid)
        self.assertEqual(list_matches[0].winner.id, domain_match_5.winner.id)
        self.assertEqual(list_matches[1].winner.id, domain_match_4.winner.id)


        self.assertEqual(total_count_2, 3)
        self.assertEqual(len(list_matches_2), 1)
        self.assertEqual(list_matches_2[0].uuid, domain_match_2.uuid)
        self.assertEqual(list_matches[0].winner.id, domain_match_2.winner.id)








