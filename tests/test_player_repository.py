import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from orm_models.base import Base
from orm_models.player_model import PlayerModel
from models.player import Player
from repositories.player_repository import PlayerRepository
from mappers.player_mapper import PlayerMapper


class TestPlayerRepository(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """Специальный метод unittest, который выполняется один раз перед всеми тестами класса."""
        cls.engine = create_engine('sqlite:///:memory:') # Engine—это объект,через который SQLAlchemy получает доступ к базе данных
        Base.metadata.create_all(cls.engine) # Base.metadata содержит описание всех зарегистрированных SQLAlchemy-моделей
        cls.SessionFactory = sessionmaker() # Здесь создаётся фабрика Session, а не сама Session.

    @classmethod
    def tearDownClass(cls) -> None:
        """Аналог setUpClass(), только выполняется один раз после всех тестов."""
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose() #

    def setUp(self) -> None:
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()

        self.session = self.SessionFactory(bind=self.connection)
        self.repository = PlayerRepository(self.session, PlayerMapper())

    def tearDown(self) -> None:
        self.session.close()
        self.transaction.rollback()
        self.connection.close()


    def test_save_new_player(self) -> None:
        new_player = Player(name="Alex", ID=None)

        saved_player = self.repository.save(new_player)

        self.assertIsNotNone(saved_player.id, "ID player")
        self.assertEqual(saved_player.name, "Alex")

        db_player = self.session.get(PlayerModel, saved_player.id)

        self.assertIsNotNone(db_player, "Player is exist")
        self.assertEqual(db_player.name, "Alex")
        self.assertEqual(db_player.normalized_name, "alex")

    def test_find_exist_player_by_name(self) -> None:
        test_db_player = PlayerModel(name="Alex", normalized_name="alex")
        self.session.add(test_db_player)
        self.session.flush()
        cases = [
            ("Alex", test_db_player),
            ("David", None)
        ]

        for name, player in cases:
            with self.subTest(f"Проверка игрока в БД {name}"):
                found_player = self.repository.find_player_by_name(name)

                if player is None:
                    self.assertIsNone(found_player)
                else:
                    self.assertIsNotNone(found_player)
                    self.assertEqual(found_player.id, player.id)
                    self.assertEqual(found_player.name, name)

    def test_find_player_by_name_with_another_register(self) -> None:
        test_db_player = PlayerModel(name="Alex", normalized_name="alex")
        self.session.add(test_db_player)
        self.session.flush()
        cases = [
            ("Alex", test_db_player),
            ("alex", test_db_player),
            ("ALEX", test_db_player)
        ]

        for name, player in cases:
            with self.subTest(f"Проверка игрока в БД {name}"):
                found_player = self.repository.find_player_by_name(name)

                self.assertIsNotNone(found_player)
                self.assertEqual(found_player.id, test_db_player.id)
                self.assertEqual(found_player.name, "Alex")

    def test_find_or_create_player_find_player(self) -> None:
        player_model = PlayerModel(id=1, name="Alex", normalized_name="alex")
        self.session.add(player_model)
        self.session.flush()
        domain_player = Player(name="Alex", ID=1)
        name = "aLEx"

        player_model_in_db = self.session.query(PlayerModel).filter(PlayerModel.normalized_name == name.lower()).first()
        result = self.repository.find_or_create_player(name)

        self.assertIsNotNone(player_model_in_db)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, domain_player.id)
        self.assertEqual(result.name, domain_player.name)

    def test_find_or_create_player_create_player(self) -> None:
        name = "Alex"
        player_model = self.session.query(PlayerModel).filter(PlayerModel.normalized_name == name.lower()).first()

        result = self.repository.find_or_create_player(name)
        player_model_in_db = self.session.query(PlayerModel).filter(PlayerModel.normalized_name == name.lower()).first()

        self.assertIsNone(player_model)
        self.assertIsNotNone(result)
        self.assertIsNotNone(player_model_in_db)
        self.assertEqual(result.name, player_model_in_db.name)
        self.assertEqual(player_model_in_db.normalized_name, name.lower())





































