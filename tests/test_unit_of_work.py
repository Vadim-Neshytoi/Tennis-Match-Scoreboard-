import unittest
from unittest.mock import MagicMock
from unit_of_work.unit_of_work import UnitOfWork


class UnitOfWorkTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_session_factory = MagicMock()
        self.mock_session = MagicMock()

        self.mock_session_factory.return_value = self.mock_session

        self.uow = UnitOfWork(self.mock_session_factory)

    def test_initializes_session_and_repositories_on_enter(self) -> None:
        self.assertIsNone(self.uow._session)

        with self.uow as active_uow:
            self.mock_session.in_transaction.return_value = False

            self.assertIs(active_uow, self.uow)
            self.mock_session_factory.assert_called_once()
            self.assertIs(self.uow._session, self.mock_session)
            self.assertIsNotNone(active_uow.player_repo)
            self.assertIsNotNone(active_uow.match_repo)
        self.mock_session.close.assert_called_once()

    def test_successful_commit_triggers_session_commit(self) -> None:
        self.mock_session.in_transaction.return_value = False
        with self.uow:
            self.uow.commit()

        self.mock_session.commit.assert_called_once()
        self.mock_session.rollback.assert_not_called()
        self.mock_session.close.assert_called_once()

    def test_exception_inside_with_triggers_automatic_rollback(self) -> None:
        with self.assertRaises(ValueError):
            with self.uow:
                raise ValueError("Boom")

        self.mock_session_factory.assert_called_once()
        self.assertIs(self.uow._session, self.mock_session)
        self.mock_session.rollback.assert_called_once()
        self.mock_session.commit.assert_not_called()
        self.mock_session.close.assert_called_once()

    def test_without_explicit_commit_does_automatic_rollback(self) -> None:
        self.mock_session.in_transaction.return_value = True
        with self.uow:
            pass

        self.mock_session.commit.assert_not_called()
        self.mock_session.rollback.assert_called_once()
        self.mock_session.close.assert_called_once()

    def test_commit_before_enter_raises_runtime_error(self) -> None:
        with self.assertRaises(RuntimeError):
            self.uow.commit()

        self.mock_session_factory.assert_not_called()
























