from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.tools.get_transactions import GetTransactionsToolUseCase
from modules.transactions.domains import TransactionDomain


class TestGetTransactionsToolUseCase(TestCase):
    """Test GetTransactionsToolUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_transaction_repository = Mock()
        self.mock_transaction_serializer = Mock()
        self.mock_transaction_factory = Mock()
        self.user_id = 1

        self.use_case = GetTransactionsToolUseCase(
            transaction_repository=self.mock_transaction_repository,
            transaction_serializer=self.mock_transaction_serializer,
            transaction_factory=self.mock_transaction_factory,
            user_id=self.user_id,
        )

    def test_get_transactions_with_all_filters(self):
        """Test getting transactions with all filters."""
        # Arrange
        transaction_type = "outgoing"
        due_date_start = "2026-03-01"
        due_date_end = "2026-03-31"

        mock_transactions = [
            Mock(spec=TransactionDomain),
            Mock(spec=TransactionDomain),
        ]

        self.mock_transaction_repository.filter.return_value = mock_transactions
        self.mock_transaction_serializer.serialize_many_for_tool.return_value = "Transaction 1: $100.00\nTransaction 2: $50.00"

        # Act
        result = self.use_case.execute(transaction_type, due_date_start, due_date_end)

        # Assert
        self.mock_transaction_repository.filter.assert_called_once()
        
        # Verify filters
        call_args = self.mock_transaction_repository.filter.call_args
        filters = call_args[0][0]
        self.assertEqual(filters["user_id"], self.user_id)
        self.assertEqual(filters["due_date__gte"], due_date_start)
        self.assertEqual(filters["due_date__lte"], due_date_end)
        self.assertEqual(filters["transaction_type"], transaction_type)

        self.mock_transaction_serializer.serialize_many_for_tool.assert_called_once_with(mock_transactions)
        self.assertEqual(result, "Transaction 1: $100.00\nTransaction 2: $50.00")

    def test_get_transactions_without_transaction_type(self):
        """Test getting transactions without transaction type filter."""
        # Arrange
        due_date_start = "2026-03-01"
        due_date_end = "2026-03-31"

        mock_transactions = [Mock(spec=TransactionDomain)]

        self.mock_transaction_repository.filter.return_value = mock_transactions
        self.mock_transaction_serializer.serialize_many_for_tool.return_value = "All transactions"

        # Act
        result = self.use_case.execute(None, due_date_start, due_date_end)

        # Assert
        self.mock_transaction_repository.filter.assert_called_once()
        
        # Verify filters don't include transaction_type
        call_args = self.mock_transaction_repository.filter.call_args
        filters = call_args[0][0]
        self.assertNotIn("transaction_type", filters)
        self.assertEqual(filters["user_id"], self.user_id)
        self.assertEqual(filters["due_date__gte"], due_date_start)
        self.assertEqual(filters["due_date__lte"], due_date_end)

    def test_get_transactions_incoming_type(self):
        """Test getting incoming transactions."""
        # Arrange
        transaction_type = "incoming"
        due_date_start = "2026-03-01"
        due_date_end = "2026-03-31"

        mock_transactions = [Mock(spec=TransactionDomain)]

        self.mock_transaction_repository.filter.return_value = mock_transactions
        self.mock_transaction_serializer.serialize_many_for_tool.return_value = "Incoming transactions"

        # Act
        result = self.use_case.execute(transaction_type, due_date_start, due_date_end)

        # Assert
        call_args = self.mock_transaction_repository.filter.call_args
        filters = call_args[0][0]
        self.assertEqual(filters["transaction_type"], "incoming")

    def test_get_transactions_empty_result(self):
        """Test getting transactions when no results are found."""
        # Arrange
        due_date_start = "2026-03-01"
        due_date_end = "2026-03-31"

        self.mock_transaction_repository.filter.return_value = []
        self.mock_transaction_serializer.serialize_many_for_tool.return_value = ""

        # Act
        result = self.use_case.execute(None, due_date_start, due_date_end)

        # Assert
        self.mock_transaction_repository.filter.assert_called_once()
        self.mock_transaction_serializer.serialize_many_for_tool.assert_called_once_with([])
        self.assertEqual(result, "")

    def test_get_transactions_method_alias(self):
        """Test that get_transactions method works as an alias to execute."""
        # Arrange
        transaction_type = "outgoing"
        due_date_start = "2026-03-01"
        due_date_end = "2026-03-31"

        self.mock_transaction_repository.filter.return_value = []
        self.mock_transaction_serializer.serialize_many_for_tool.return_value = ""

        # Act
        result = self.use_case.get_transactions(transaction_type, due_date_start, due_date_end)

        # Assert
        self.mock_transaction_repository.filter.assert_called_once()
        self.assertEqual(result, "")

