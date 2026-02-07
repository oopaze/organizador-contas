from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.actor.get import GetActorUseCase
from modules.transactions.domains import ActorDomain, SubTransactionDomain


class TestGetActorUseCase(TestCase):
    """Test GetActorUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_actor_repository = Mock()
        self.mock_actor_serializer = Mock()
        self.mock_sub_transaction_repository = Mock()
        self.mock_sub_transaction_serializer = Mock()

        self.use_case = GetActorUseCase(
            actor_repository=self.mock_actor_repository,
            actor_serializer=self.mock_actor_serializer,
            sub_transaction_repository=self.mock_sub_transaction_repository,
            sub_transaction_serializer=self.mock_sub_transaction_serializer,
        )

    def test_get_actor_with_sub_transactions(self):
        """Test getting an actor with sub-transactions."""
        # Arrange
        actor_id = 1
        user_id = 1
        due_date = "2026-03"

        mock_actor = Mock(spec=ActorDomain)
        mock_sub_transactions = [
            Mock(spec=SubTransactionDomain),
            Mock(spec=SubTransactionDomain),
        ]

        self.mock_actor_repository.get.return_value = mock_actor
        self.mock_sub_transaction_repository.get_by_actor_id.return_value = mock_sub_transactions
        self.mock_actor_serializer.serialize.return_value = {"id": actor_id, "name": "John Doe"}
        self.mock_sub_transaction_serializer.serialize.side_effect = [
            {"id": 1, "description": "Sub 1"},
            {"id": 2, "description": "Sub 2"},
        ]

        # Act
        result = self.use_case.execute(actor_id, user_id, due_date)

        # Assert
        self.mock_actor_repository.get.assert_called_once_with(actor_id, user_id)
        self.mock_sub_transaction_repository.get_by_actor_id.assert_called_once_with(actor_id, user_id, due_date)
        mock_actor.set_sub_transactions.assert_called_once_with(mock_sub_transactions)
        self.assertEqual(len(result["sub_transactions"]), 2)
        self.assertEqual(result["id"], actor_id)

    def test_get_actor_without_due_date(self):
        """Test getting an actor without due date filter."""
        # Arrange
        actor_id = 1
        user_id = 1

        mock_actor = Mock(spec=ActorDomain)
        mock_sub_transactions = []

        self.mock_actor_repository.get.return_value = mock_actor
        self.mock_sub_transaction_repository.get_by_actor_id.return_value = mock_sub_transactions
        self.mock_actor_serializer.serialize.return_value = {"id": actor_id, "name": "John Doe"}

        # Act
        result = self.use_case.execute(actor_id, user_id)

        # Assert
        self.mock_actor_repository.get.assert_called_once_with(actor_id, user_id)
        self.mock_sub_transaction_repository.get_by_actor_id.assert_called_once_with(actor_id, user_id, None)
        mock_actor.set_sub_transactions.assert_called_once_with(mock_sub_transactions)
        self.assertEqual(result["sub_transactions"], [])

    def test_get_actor_serializes_without_actor_in_sub_transactions(self):
        """Test that sub-transactions are serialized with include_actor=False."""
        # Arrange
        actor_id = 1
        user_id = 1

        mock_actor = Mock(spec=ActorDomain)
        mock_sub_transaction = Mock(spec=SubTransactionDomain)

        self.mock_actor_repository.get.return_value = mock_actor
        self.mock_sub_transaction_repository.get_by_actor_id.return_value = [mock_sub_transaction]
        self.mock_actor_serializer.serialize.return_value = {"id": actor_id}
        self.mock_sub_transaction_serializer.serialize.return_value = {"id": 1}

        # Act
        self.use_case.execute(actor_id, user_id)

        # Assert
        # Verify that serialize was called with include_actor=False
        self.mock_sub_transaction_serializer.serialize.assert_called_once_with(mock_sub_transaction, include_actor=False)

