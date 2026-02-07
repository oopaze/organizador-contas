from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.transaction.update import UpdateTransactionUseCase
from modules.transactions.domains import TransactionDomain, SubTransactionDomain


class TestUpdateTransactionUseCase(TestCase):
    """Test UpdateTransactionUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_transaction_repository = Mock()
        self.mock_transaction_serializer = Mock()
        self.mock_sub_transaction_repository = Mock()

        self.use_case = UpdateTransactionUseCase(
            transaction_repository=self.mock_transaction_repository,
            transaction_serializer=self.mock_transaction_serializer,
            sub_transaction_repository=self.mock_sub_transaction_repository,
        )

    def test_update_simple_transaction(self):
        """Test updating a simple non-recurrent transaction."""
        # Arrange
        transaction_id = 1
        data = {
            "user_id": 1,
            "due_date": "2026-03-20",
            "total_amount": 200.00,
            "transaction_identifier": "Updated Bill",
            "transaction_type": "outgoing",
        }

        mock_transaction = TransactionDomain(
            id=transaction_id,
            due_date="2026-03-15",
            total_amount=150.00,
            transaction_identifier="Original Bill",
            transaction_type="outgoing",
            user_id=1,
            is_recurrent=False,
        )

        updated_mock_transaction = TransactionDomain(
            id=transaction_id,
            due_date="2026-03-20",
            total_amount=200.00,
            transaction_identifier="Updated Bill",
            transaction_type="outgoing",
            user_id=1,
            is_recurrent=False,
        )

        self.mock_transaction_repository.get.return_value = mock_transaction
        self.mock_transaction_repository.get_children_transactions.return_value = []
        self.mock_sub_transaction_repository.get_all_by_transaction_id.return_value = []
        self.mock_transaction_repository.update.return_value = updated_mock_transaction
        self.mock_transaction_serializer.serialize.return_value = {"id": 1, "transaction_identifier": "Updated Bill"}

        # Act
        result = self.use_case.execute(transaction_id, data)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(transaction_id, data["user_id"])
        self.mock_transaction_repository.update.assert_called_once()
        self.mock_transaction_serializer.serialize.assert_called_once_with(updated_mock_transaction)
        self.assertEqual(result, {"id": 1, "transaction_identifier": "Updated Bill"})

    def test_update_transaction_with_single_sub_transaction(self):
        """Test updating a transaction that has a single sub-transaction."""
        # Arrange
        transaction_id = 1
        data = {
            "user_id": 1,
            "due_date": "2026-03-20",
            "total_amount": 200.00,
            "transaction_identifier": "Updated Bill",
            "transaction_type": "outgoing",
        }

        mock_transaction = TransactionDomain(
            id=transaction_id,
            due_date="2026-03-15",
            total_amount=150.00,
            transaction_identifier="Original Bill",
            transaction_type="outgoing",
            user_id=1,
            is_recurrent=False,
        )

        mock_sub_transaction = SubTransactionDomain(
            id=1,
            date="2026-03-15",
            description="Original Bill",
            amount=150.00,
            installment_info="1/1",
        )

        updated_mock_transaction = TransactionDomain(
            id=transaction_id,
            due_date="2026-03-20",
            total_amount=200.00,
            transaction_identifier="Updated Bill",
            transaction_type="outgoing",
            user_id=1,
            is_recurrent=False,
        )

        self.mock_transaction_repository.get.return_value = mock_transaction
        self.mock_transaction_repository.get_children_transactions.return_value = []
        self.mock_sub_transaction_repository.get_all_by_transaction_id.return_value = [mock_sub_transaction]
        self.mock_transaction_repository.update.return_value = updated_mock_transaction
        self.mock_transaction_serializer.serialize.return_value = {"id": 1, "transaction_identifier": "Updated Bill"}

        # Act
        result = self.use_case.execute(transaction_id, data)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(transaction_id, data["user_id"])
        # Sub-transaction should be updated
        self.assertEqual(self.mock_sub_transaction_repository.get_all_by_transaction_id.call_count, 2)
        self.mock_transaction_repository.update.assert_called_once()
        self.assertEqual(result, {"id": 1, "transaction_identifier": "Updated Bill"})

    def test_update_recurrent_transaction_with_children(self):
        """Test updating a recurrent transaction updates all children."""
        # Arrange
        transaction_id = 1
        data = {
            "user_id": 1,
            "due_date": "2026-03-20",
            "total_amount": 200.00,
            "transaction_identifier": "Updated Subscription",
            "transaction_type": "outgoing",
        }

        mock_transaction = TransactionDomain(
            id=transaction_id,
            due_date="2026-03-15",
            total_amount=150.00,
            transaction_identifier="Original Subscription",
            transaction_type="outgoing",
            user_id=1,
            is_recurrent=True,
            recurrence_count=3,
        )

        # Mock child transactions
        mock_children = [
            TransactionDomain(id=2, due_date="2026-04-15", user_id=1, is_recurrent=True),
            TransactionDomain(id=3, due_date="2026-05-15", user_id=1, is_recurrent=True),
        ]

        self.mock_transaction_repository.get.return_value = mock_transaction
        self.mock_transaction_repository.get_children_transactions.return_value = mock_children
        self.mock_sub_transaction_repository.get_all_by_transaction_id.return_value = []
        self.mock_transaction_repository.update_many.return_value = mock_children
        self.mock_transaction_repository.update.return_value = mock_transaction
        self.mock_transaction_serializer.serialize.return_value = {"id": 1, "transaction_identifier": "Updated Subscription"}

        # Act
        result = self.use_case.execute(transaction_id, data)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(transaction_id, data["user_id"])
        self.mock_transaction_repository.get_children_transactions.assert_called()
        self.mock_transaction_repository.update_many.assert_called_once_with(mock_children)
        self.assertEqual(result, {"id": 1, "transaction_identifier": "Updated Subscription"})

    def test_calculate_next_due_date(self):
        """Test date calculation for updating recurrent transactions."""
        # Test moving 0 months (same month)
        next_date = self.use_case.calculate_next_due_date("2026-03-15", 0)
        self.assertEqual(next_date, "2026-03-15")

        # Test moving 1 month
        next_date = self.use_case.calculate_next_due_date("2026-03-15", 1)
        self.assertEqual(next_date, "2026-04-15")

        # Test moving 2 months
        next_date = self.use_case.calculate_next_due_date("2026-03-15", 2)
        self.assertEqual(next_date, "2026-05-15")

