from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.sub_transaction.delete import DeleteSubTransactionUseCase
from modules.transactions.domains import SubTransactionDomain


class TestDeleteSubTransactionUseCase(TestCase):
    """Test DeleteSubTransactionUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_sub_transaction_repository = Mock()

        self.use_case = DeleteSubTransactionUseCase(
            sub_transaction_repository=self.mock_sub_transaction_repository,
        )

    def test_delete_sub_transaction(self):
        """Test deleting a sub-transaction."""
        # Arrange
        sub_transaction_id = 1
        user_id = 1

        mock_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_sub_transaction.id = sub_transaction_id

        self.mock_sub_transaction_repository.get.return_value = mock_sub_transaction

        # Act
        self.use_case.execute(sub_transaction_id, user_id)

        # Assert
        self.mock_sub_transaction_repository.get.assert_called_once_with(sub_transaction_id, user_id)
        self.mock_sub_transaction_repository.delete.assert_called_once_with(sub_transaction_id)

    def test_delete_sub_transaction_different_user(self):
        """Test deleting a sub-transaction for a different user."""
        # Arrange
        sub_transaction_id = 2
        user_id = 2

        mock_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_sub_transaction.id = sub_transaction_id

        self.mock_sub_transaction_repository.get.return_value = mock_sub_transaction

        # Act
        self.use_case.execute(sub_transaction_id, user_id)

        # Assert
        self.mock_sub_transaction_repository.get.assert_called_once_with(sub_transaction_id, user_id)
        self.mock_sub_transaction_repository.delete.assert_called_once_with(sub_transaction_id)

