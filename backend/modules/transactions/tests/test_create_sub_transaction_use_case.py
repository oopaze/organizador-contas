from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.sub_transaction.create import CreateSubTransactionUseCase
from modules.transactions.domains import SubTransactionDomain, TransactionDomain, ActorDomain


class TestCreateSubTransactionUseCase(TestCase):
    """Test CreateSubTransactionUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_transaction_repository = Mock()
        self.mock_actor_repository = Mock()
        self.mock_sub_transaction_repository = Mock()
        self.mock_sub_transaction_serializer = Mock()
        self.mock_sub_transaction_factory = Mock()

        self.use_case = CreateSubTransactionUseCase(
            transaction_repository=self.mock_transaction_repository,
            actor_repository=self.mock_actor_repository,
            sub_transaction_repository=self.mock_sub_transaction_repository,
            sub_transaction_serializer=self.mock_sub_transaction_serializer,
            sub_transaction_factory=self.mock_sub_transaction_factory,
        )

    def test_create_sub_transaction_with_actor(self):
        """Test creating a sub-transaction with an actor."""
        # Arrange
        user_id = 1
        data = {
            "transaction_id": 1,
            "actor": 1,
            "description": "Grocery shopping",
            "amount": 50.00,
            "date": "2026-03-15",
        }

        mock_transaction = Mock(spec=TransactionDomain)
        mock_actor = Mock(spec=ActorDomain)
        mock_sub_transaction = SubTransactionDomain(
            id=1,
            description="Grocery shopping",
            amount=50.00,
            date="2026-03-15",
        )

        self.mock_transaction_repository.get.return_value = mock_transaction
        self.mock_actor_repository.get.return_value = mock_actor
        self.mock_sub_transaction_factory.build.return_value = mock_sub_transaction
        self.mock_sub_transaction_repository.create.return_value = mock_sub_transaction
        self.mock_sub_transaction_serializer.serialize.return_value = {"id": 1, "description": "Grocery shopping"}

        # Act
        result = self.use_case.execute(data, user_id)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(data["transaction_id"], user_id)
        self.mock_actor_repository.get.assert_called_once_with(data["actor"], user_id)
        self.mock_sub_transaction_factory.build.assert_called_once_with(data, mock_transaction, mock_actor)
        self.mock_sub_transaction_repository.create.assert_called_once_with(mock_sub_transaction)
        self.mock_sub_transaction_serializer.serialize.assert_called_once_with(mock_sub_transaction)
        self.assertEqual(result, {"id": 1, "description": "Grocery shopping"})

    def test_create_sub_transaction_without_actor(self):
        """Test creating a sub-transaction without an actor."""
        # Arrange
        user_id = 1
        data = {
            "transaction_id": 1,
            "description": "Utility bill",
            "amount": 100.00,
            "date": "2026-03-15",
        }

        mock_transaction = Mock(spec=TransactionDomain)
        mock_sub_transaction = SubTransactionDomain(
            id=2,
            description="Utility bill",
            amount=100.00,
            date="2026-03-15",
        )

        self.mock_transaction_repository.get.return_value = mock_transaction
        self.mock_sub_transaction_factory.build.return_value = mock_sub_transaction
        self.mock_sub_transaction_repository.create.return_value = mock_sub_transaction
        self.mock_sub_transaction_serializer.serialize.return_value = {"id": 2, "description": "Utility bill"}

        # Act
        result = self.use_case.execute(data, user_id)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(data["transaction_id"], user_id)
        self.mock_actor_repository.get.assert_not_called()
        self.mock_sub_transaction_factory.build.assert_called_once_with(data, mock_transaction, None)
        self.mock_sub_transaction_repository.create.assert_called_once_with(mock_sub_transaction)
        self.assertEqual(result, {"id": 2, "description": "Utility bill"})

