"""
Unit tests for TransposeFileBillToModelsUseCase.

These tests verify that the use case correctly transposes file bill data to models.
All external dependencies are mocked.
"""
from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.file_reader.use_cases.transpose_file_bill_to_models import TransposeFileBillToModelsUseCase
from modules.file_reader.domains.file import FileDomain
from modules.file_reader.domains.bill import BillDomain
from modules.file_reader.domains.bill_sub_transaction import BillSubTransactionDomain


class TestTransposeFileBillToModelsUseCase(SimpleTestCase):
    """Test TransposeFileBillToModelsUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_bill_repository = Mock()
        self.mock_bill_factory = Mock()
        self.mock_bill_serializer = Mock()
        self.mock_sub_transaction_repository = Mock()
        self.mock_sub_transaction_factory = Mock()
        self.mock_file_repository = Mock()
        self.mock_recalculate_use_case = Mock()

        self.use_case = TransposeFileBillToModelsUseCase(
            bill_repository=self.mock_bill_repository,
            bill_factory=self.mock_bill_factory,
            bill_serializer=self.mock_bill_serializer,
            bill_sub_transaction_repository=self.mock_sub_transaction_repository,
            bill_sub_transaction_factory=self.mock_sub_transaction_factory,
            file_repository=self.mock_file_repository,
            recalculate_amount_use_case=self.mock_recalculate_use_case,
        )

    def test_execute_for_single_bill(self):
        """Test that execute processes a single bill correctly."""
        # Arrange
        file_id = "123"
        user_id = 1
        
        mock_file = Mock(spec=FileDomain)
        mock_file.get_response.return_value = {
            "bill_identifier": "Credit Card",
            "total_amount": 500.00,
            "due_date": "2026-03-15",
            "transactions": []
        }
        
        mock_bill = Mock(spec=BillDomain)
        mock_bill.id = "bill_123"
        
        self.mock_file_repository.get.return_value = mock_file
        self.mock_bill_factory.build_from_file.return_value = mock_bill
        self.mock_bill_repository.create.return_value = mock_bill
        self.mock_sub_transaction_factory.build_many_from_file.return_value = []

        # Act
        self.use_case.execute(file_id, user_id)

        # Assert
        self.mock_file_repository.get.assert_called_once_with(file_id)
        self.mock_bill_factory.build_from_file.assert_called_once()
        self.mock_bill_repository.create.assert_called_once_with(mock_bill, user_id)
        self.mock_sub_transaction_repository.create_many.assert_called_once_with([])

    def test_execute_for_bill_with_sub_transactions(self):
        """Test that execute processes bill with sub-transactions."""
        # Arrange
        file_id = "123"
        user_id = 1
        
        mock_file = Mock(spec=FileDomain)
        response = {
            "bill_identifier": "Credit Card",
            "total_amount": 500.00,
            "due_date": "2026-03-15",
            "transactions": [
                {"description": "Purchase 1", "amount": 250.00},
                {"description": "Purchase 2", "amount": 250.00},
            ]
        }
        mock_file.get_response.return_value = response
        
        mock_bill = Mock(spec=BillDomain)
        mock_bill.id = "bill_123"
        mock_sub_trans = [Mock(spec=BillSubTransactionDomain), Mock(spec=BillSubTransactionDomain)]
        
        self.mock_file_repository.get.return_value = mock_file
        self.mock_bill_factory.build_from_file.return_value = mock_bill
        self.mock_bill_repository.create.return_value = mock_bill
        self.mock_sub_transaction_factory.build_many_from_file.return_value = mock_sub_trans

        # Act
        self.use_case.execute(file_id, user_id)

        # Assert
        self.mock_sub_transaction_factory.build_many_from_file.assert_called_once_with(
            mock_file, mock_bill, response
        )
        self.mock_sub_transaction_repository.create_many.assert_called_once_with(mock_sub_trans)

    def test_execute_for_multiple_bills(self):
        """Test that execute processes multiple bills from a list response."""
        # Arrange
        file_id = "123"
        user_id = 1
        
        mock_file = Mock(spec=FileDomain)
        mock_file.get_response.return_value = [
            {"bill_identifier": "Bill 1", "total_amount": 100.00, "due_date": "2026-03-15", "transactions": []},
            {"bill_identifier": "Bill 2", "total_amount": 200.00, "due_date": "2026-03-20", "transactions": []},
        ]
        
        mock_bill1 = Mock(spec=BillDomain)
        mock_bill1.id = "bill_1"
        mock_bill2 = Mock(spec=BillDomain)
        mock_bill2.id = "bill_2"
        
        self.mock_file_repository.get.return_value = mock_file
        self.mock_bill_factory.build_from_file.side_effect = [mock_bill1, mock_bill2]
        self.mock_bill_repository.create.side_effect = [mock_bill1, mock_bill2]
        self.mock_sub_transaction_factory.build_many_from_file.return_value = []

        # Act
        self.use_case.execute(file_id, user_id)

        # Assert
        self.assertEqual(self.mock_bill_factory.build_from_file.call_count, 2)
        self.assertEqual(self.mock_bill_repository.create.call_count, 2)
        self.assertEqual(self.mock_sub_transaction_repository.create_many.call_count, 2)

    def test_execute_with_create_in_future_months_false(self):
        """Test that execute does not create future transactions when flag is False."""
        # Arrange
        file_id = "123"
        user_id = 1
        
        mock_file = Mock(spec=FileDomain)
        mock_file.get_response.return_value = {
            "bill_identifier": "Credit Card",
            "total_amount": 500.00,
            "due_date": "2026-03-15",
            "transactions": [
                {"description": "Item", "amount": 100.00, "installment_info": "1/12"}
            ]
        }
        
        mock_bill = Mock(spec=BillDomain)
        mock_bill.id = "bill_123"
        
        self.mock_file_repository.get.return_value = mock_file
        self.mock_bill_factory.build_from_file.return_value = mock_bill
        self.mock_bill_repository.create.return_value = mock_bill
        self.mock_sub_transaction_factory.build_many_from_file.return_value = []

        # Act
        self.use_case.execute(file_id, user_id, create_in_future_months=False)

        # Assert
        # Should only create one bill (the current one, not future installments)
        self.assertEqual(self.mock_bill_repository.create.call_count, 1)

