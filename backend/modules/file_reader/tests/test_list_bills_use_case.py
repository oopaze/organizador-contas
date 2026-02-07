"""
Unit tests for ListBillsUseCase.

These tests verify that the use case correctly retrieves and serializes bills.
All external dependencies are mocked.
"""
from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.file_reader.use_cases.list_bills import ListBillsUseCase
from modules.file_reader.domains.bill import BillDomain


class TestListBillsUseCase(SimpleTestCase):
    """Test ListBillsUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = Mock()
        self.mock_serializer = Mock()

        self.use_case = ListBillsUseCase(
            bill_repository=self.mock_repository,
            bill_serializer=self.mock_serializer,
        )

    def test_execute_returns_serialized_bills(self):
        """Test that execute returns a list of serialized bills."""
        # Arrange
        mock_bill1 = Mock(spec=BillDomain)
        mock_bill2 = Mock(spec=BillDomain)
        self.mock_repository.get_all.return_value = [mock_bill1, mock_bill2]
        
        self.mock_serializer.serialize.side_effect = [
            {"id": 1, "identifier": "Bill 1"},
            {"id": 2, "identifier": "Bill 2"},
        ]

        # Act
        result = self.use_case.execute()

        # Assert
        self.mock_repository.get_all.assert_called_once()
        self.assertEqual(self.mock_serializer.serialize.call_count, 2)
        self.mock_serializer.serialize.assert_any_call(mock_bill1, include_transactions=False)
        self.mock_serializer.serialize.assert_any_call(mock_bill2, include_transactions=False)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[1]["id"], 2)

    def test_execute_with_empty_bills(self):
        """Test that execute handles empty bill list."""
        # Arrange
        self.mock_repository.get_all.return_value = []

        # Act
        result = self.use_case.execute()

        # Assert
        self.mock_repository.get_all.assert_called_once()
        self.mock_serializer.serialize.assert_not_called()
        self.assertEqual(result, [])

    def test_execute_calls_serializer_without_transactions(self):
        """Test that serializer is called with include_transactions=False."""
        # Arrange
        mock_bill = Mock(spec=BillDomain)
        self.mock_repository.get_all.return_value = [mock_bill]
        self.mock_serializer.serialize.return_value = {"id": 1}

        # Act
        self.use_case.execute()

        # Assert
        self.mock_serializer.serialize.assert_called_once_with(
            mock_bill, 
            include_transactions=False
        )

