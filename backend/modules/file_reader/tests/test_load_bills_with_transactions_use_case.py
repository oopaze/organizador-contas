"""
Unit tests for LoadBillsWithTransactionsUseCase.

These tests verify that the use case correctly loads a bill with its transactions.
All external dependencies are mocked.
"""
from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.file_reader.use_cases.load_bills_with_transactions import LoadBillsWithTransactionsUseCase
from modules.file_reader.domains.bill import BillDomain
from modules.file_reader.domains.bill_sub_transaction import BillSubTransactionDomain


class TestLoadBillsWithTransactionsUseCase(SimpleTestCase):
    """Test LoadBillsWithTransactionsUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_bill_repository = Mock()
        self.mock_sub_transaction_repository = Mock()
        self.mock_serializer = Mock()

        self.use_case = LoadBillsWithTransactionsUseCase(
            bill_repository=self.mock_bill_repository,
            bill_sub_transaction_repository=self.mock_sub_transaction_repository,
            bill_serializer=self.mock_serializer,
        )

    def test_execute_loads_bill_with_transactions(self):
        """Test that execute loads a bill and its sub-transactions."""
        # Arrange
        bill_id = "123"
        mock_bill = Mock(spec=BillDomain)
        mock_sub_transaction1 = Mock(spec=BillSubTransactionDomain)
        mock_sub_transaction2 = Mock(spec=BillSubTransactionDomain)
        
        self.mock_bill_repository.get.return_value = mock_bill
        self.mock_sub_transaction_repository.get_many_by_bill_id.return_value = [
            mock_sub_transaction1,
            mock_sub_transaction2,
        ]
        self.mock_serializer.serialize.return_value = {
            "id": bill_id,
            "transactions": [{"id": 1}, {"id": 2}]
        }

        # Act
        result = self.use_case.execute(bill_id)

        # Assert
        self.mock_bill_repository.get.assert_called_once_with(bill_id)
        self.mock_sub_transaction_repository.get_many_by_bill_id.assert_called_once_with(bill_id)
        mock_bill.set_bill_sub_transactions.assert_called_once_with([
            mock_sub_transaction1,
            mock_sub_transaction2,
        ])
        self.mock_serializer.serialize.assert_called_once_with(mock_bill)
        self.assertEqual(result["id"], bill_id)

    def test_execute_with_no_transactions(self):
        """Test that execute handles bills with no sub-transactions."""
        # Arrange
        bill_id = "456"
        mock_bill = Mock(spec=BillDomain)
        
        self.mock_bill_repository.get.return_value = mock_bill
        self.mock_sub_transaction_repository.get_many_by_bill_id.return_value = []
        self.mock_serializer.serialize.return_value = {
            "id": bill_id,
            "transactions": []
        }

        # Act
        result = self.use_case.execute(bill_id)

        # Assert
        self.mock_bill_repository.get.assert_called_once_with(bill_id)
        self.mock_sub_transaction_repository.get_many_by_bill_id.assert_called_once_with(bill_id)
        mock_bill.set_bill_sub_transactions.assert_called_once_with([])
        self.mock_serializer.serialize.assert_called_once_with(mock_bill)
        self.assertEqual(result["transactions"], [])

    def test_execute_sets_transactions_before_serializing(self):
        """Test that sub-transactions are set on the bill before serialization."""
        # Arrange
        bill_id = "789"
        mock_bill = Mock(spec=BillDomain)
        mock_sub_transactions = [Mock(spec=BillSubTransactionDomain)]
        
        self.mock_bill_repository.get.return_value = mock_bill
        self.mock_sub_transaction_repository.get_many_by_bill_id.return_value = mock_sub_transactions
        self.mock_serializer.serialize.return_value = {"id": bill_id}

        # Track call order
        call_order = []
        mock_bill.set_bill_sub_transactions.side_effect = lambda x: call_order.append("set_transactions")
        self.mock_serializer.serialize.side_effect = lambda x: (call_order.append("serialize"), {"id": bill_id})[1]

        # Act
        self.use_case.execute(bill_id)

        # Assert
        self.assertEqual(call_order, ["set_transactions", "serialize"])

