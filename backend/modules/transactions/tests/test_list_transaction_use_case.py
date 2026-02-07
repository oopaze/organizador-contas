from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.transaction.list import ListTransactionsUseCase
from modules.transactions.domains import TransactionDomain


class TestListTransactionsUseCase(TestCase):
    """Test ListTransactionsUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_transaction_repository = Mock()
        self.mock_transaction_serializer = Mock()

        self.use_case = ListTransactionsUseCase(
            transaction_repository=self.mock_transaction_repository,
            transaction_serializer=self.mock_transaction_serializer,
        )

    def test_list_all_transactions_no_filters(self):
        """Test listing all transactions without filters."""
        # Arrange
        mock_transactions = [
            TransactionDomain(
                id=1,
                due_date="2026-03-15",
                total_amount=150.00,
                transaction_identifier="Bill 1",
                transaction_type="outgoing",
                user_id=1,
            ),
            TransactionDomain(
                id=2,
                due_date="2026-03-20",
                total_amount=200.00,
                transaction_identifier="Bill 2",
                transaction_type="outgoing",
                user_id=1,
            ),
        ]

        self.mock_transaction_repository.filter.return_value = mock_transactions
        self.mock_transaction_serializer.serialize.side_effect = [
            {"id": 1, "transaction_identifier": "Bill 1"},
            {"id": 2, "transaction_identifier": "Bill 2"},
        ]

        # Act
        result = self.use_case.execute()

        # Assert
        self.mock_transaction_repository.filter.assert_called_once_with(filters={})
        self.assertEqual(self.mock_transaction_serializer.serialize.call_count, 2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[1]["id"], 2)

    def test_list_transactions_with_type_filter(self):
        """Test listing transactions filtered by type."""
        # Arrange
        filters = {"transaction_type": "incoming"}
        
        mock_transactions = [
            TransactionDomain(
                id=1,
                due_date="2026-03-01",
                total_amount=5000.00,
                transaction_identifier="Salary",
                transaction_type="incoming",
                user_id=1,
                is_salary=True,
            ),
        ]

        self.mock_transaction_repository.filter.return_value = mock_transactions
        self.mock_transaction_serializer.serialize.return_value = {"id": 1, "transaction_identifier": "Salary"}

        # Act
        result = self.use_case.execute(filters)

        # Assert
        self.mock_transaction_repository.filter.assert_called_once_with(filters=filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["transaction_identifier"], "Salary")

    def test_list_transactions_with_date_filter(self):
        """Test listing transactions filtered by due date."""
        # Arrange
        filters = {"due_date": "2026-03"}
        
        mock_transactions = [
            TransactionDomain(
                id=1,
                due_date="2026-03-15",
                total_amount=150.00,
                transaction_identifier="March Bill",
                transaction_type="outgoing",
                user_id=1,
            ),
        ]

        self.mock_transaction_repository.filter.return_value = mock_transactions
        self.mock_transaction_serializer.serialize.return_value = {"id": 1, "transaction_identifier": "March Bill"}

        # Act
        result = self.use_case.execute(filters)

        # Assert
        self.mock_transaction_repository.filter.assert_called_once_with(filters=filters)
        self.assertEqual(len(result), 1)

    def test_list_transactions_empty_result(self):
        """Test listing transactions when no results are found."""
        # Arrange
        filters = {"transaction_type": "incoming"}
        
        self.mock_transaction_repository.filter.return_value = []

        # Act
        result = self.use_case.execute(filters)

        # Assert
        self.mock_transaction_repository.filter.assert_called_once_with(filters=filters)
        self.assertEqual(len(result), 0)
        self.assertEqual(result, [])
        # Serializer should not be called when there are no transactions
        self.mock_transaction_serializer.serialize.assert_not_called()

    def test_list_transactions_with_multiple_filters(self):
        """Test listing transactions with multiple filters."""
        # Arrange
        filters = {
            "transaction_type": "outgoing",
            "due_date": "2026-03",
        }
        
        mock_transactions = [
            TransactionDomain(
                id=1,
                due_date="2026-03-15",
                total_amount=150.00,
                transaction_identifier="Filtered Bill",
                transaction_type="outgoing",
                user_id=1,
            ),
        ]

        self.mock_transaction_repository.filter.return_value = mock_transactions
        self.mock_transaction_serializer.serialize.return_value = {"id": 1, "transaction_identifier": "Filtered Bill"}

        # Act
        result = self.use_case.execute(filters)

        # Assert
        self.mock_transaction_repository.filter.assert_called_once_with(filters=filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["transaction_identifier"], "Filtered Bill")

