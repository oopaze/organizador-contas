from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.transaction.get import GetTransactionUseCase
from modules.transactions.domains import TransactionDomain, SubTransactionDomain


class TestGetTransactionUseCase(TestCase):
    """Test GetTransactionUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_transaction_repository = Mock()
        self.mock_transaction_serializer = Mock()
        self.mock_sub_transaction_repository = Mock()

        self.use_case = GetTransactionUseCase(
            transaction_repository=self.mock_transaction_repository,
            transaction_serializer=self.mock_transaction_serializer,
            sub_transaction_repository=self.mock_sub_transaction_repository,
        )

    def test_get_transaction_with_sub_transactions(self):
        """Test getting a transaction with its sub-transactions."""
        # Arrange
        transaction_id = 1
        user_id = 1

        mock_transaction = TransactionDomain(
            id=transaction_id,
            due_date="2026-03-15",
            total_amount=150.00,
            transaction_identifier="Bill with subs",
            transaction_type="outgoing",
            user_id=user_id,
        )

        mock_sub_transactions = [
            SubTransactionDomain(
                id=1,
                date="2026-03-15",
                description="Item 1",
                amount=100.00,
                installment_info="1/1",
            ),
            SubTransactionDomain(
                id=2,
                date="2026-03-15",
                description="Item 2",
                amount=50.00,
                installment_info="1/1",
            ),
        ]

        self.mock_transaction_repository.get.return_value = mock_transaction
        self.mock_sub_transaction_repository.get_all_by_transaction_id.return_value = mock_sub_transactions
        self.mock_transaction_serializer.serialize.return_value = {
            "id": 1,
            "transaction_identifier": "Bill with subs",
            "sub_transactions": [
                {"id": 1, "description": "Item 1"},
                {"id": 2, "description": "Item 2"},
            ]
        }

        # Act
        result = self.use_case.execute(transaction_id, user_id)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(transaction_id, user_id)
        self.mock_sub_transaction_repository.get_all_by_transaction_id.assert_called_once_with(transaction_id, user_id)
        self.mock_transaction_serializer.serialize.assert_called_once_with(mock_transaction)
        self.assertEqual(result["id"], 1)
        self.assertEqual(len(result["sub_transactions"]), 2)

    def test_get_transaction_without_sub_transactions(self):
        """Test getting a transaction without sub-transactions."""
        # Arrange
        transaction_id = 1
        user_id = 1

        mock_transaction = TransactionDomain(
            id=transaction_id,
            due_date="2026-03-01",
            total_amount=5000.00,
            transaction_identifier="Salary",
            transaction_type="incoming",
            user_id=user_id,
            is_salary=True,
        )

        self.mock_transaction_repository.get.return_value = mock_transaction
        self.mock_sub_transaction_repository.get_all_by_transaction_id.return_value = []
        self.mock_transaction_serializer.serialize.return_value = {
            "id": 1,
            "transaction_identifier": "Salary",
            "sub_transactions": []
        }

        # Act
        result = self.use_case.execute(transaction_id, user_id)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(transaction_id, user_id)
        self.mock_sub_transaction_repository.get_all_by_transaction_id.assert_called_once_with(transaction_id, user_id)
        self.mock_transaction_serializer.serialize.assert_called_once_with(mock_transaction)
        self.assertEqual(result["id"], 1)
        self.assertEqual(len(result["sub_transactions"]), 0)

    def test_get_transaction_sets_sub_transactions_on_domain(self):
        """Test that sub-transactions are set on the transaction domain object."""
        # Arrange
        transaction_id = 1
        user_id = 1

        mock_transaction = Mock(spec=TransactionDomain)
        mock_sub_transactions = [Mock(spec=SubTransactionDomain)]

        self.mock_transaction_repository.get.return_value = mock_transaction
        self.mock_sub_transaction_repository.get_all_by_transaction_id.return_value = mock_sub_transactions
        self.mock_transaction_serializer.serialize.return_value = {"id": 1}

        # Act
        self.use_case.execute(transaction_id, user_id)

        # Assert
        # Verify that set_sub_transactions was called on the domain object
        mock_transaction.set_sub_transactions.assert_called_once_with(mock_sub_transactions)

