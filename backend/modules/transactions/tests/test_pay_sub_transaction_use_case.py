from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.sub_transaction.pay import PaySubTransactionUseCase
from modules.transactions.domains import SubTransactionDomain


class TestPaySubTransactionUseCase(TestCase):
    """Test PaySubTransactionUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_sub_transaction_repository = Mock()

        self.use_case = PaySubTransactionUseCase(
            sub_transaction_repository=self.mock_sub_transaction_repository,
        )

    def test_pay_sub_transaction(self):
        """Test paying a sub-transaction."""
        # Arrange
        sub_transaction_id = 1
        user_id = 1

        mock_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_sub_transaction.is_paying.return_value = True

        self.mock_sub_transaction_repository.get.return_value = mock_sub_transaction

        # Act
        result = self.use_case.execute(sub_transaction_id, user_id)

        # Assert
        self.mock_sub_transaction_repository.get.assert_called_once_with(sub_transaction_id, user_id)
        mock_sub_transaction.is_paying.assert_called_once()
        mock_sub_transaction.pay.assert_called_once()
        mock_sub_transaction.unpay.assert_not_called()
        self.mock_sub_transaction_repository.update_paid_at.assert_called_once_with(mock_sub_transaction)
        self.assertEqual(result, {"message": "success"})

    def test_unpay_sub_transaction(self):
        """Test unpaying a sub-transaction."""
        # Arrange
        sub_transaction_id = 1
        user_id = 1

        mock_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_sub_transaction.is_paying.return_value = False

        self.mock_sub_transaction_repository.get.return_value = mock_sub_transaction

        # Act
        result = self.use_case.execute(sub_transaction_id, user_id)

        # Assert
        self.mock_sub_transaction_repository.get.assert_called_once_with(sub_transaction_id, user_id)
        mock_sub_transaction.is_paying.assert_called_once()
        mock_sub_transaction.unpay.assert_called_once()
        mock_sub_transaction.pay.assert_not_called()
        self.mock_sub_transaction_repository.update_paid_at.assert_called_once_with(mock_sub_transaction)
        self.assertEqual(result, {"message": "success"})

    def test_pay_sub_transaction_different_user(self):
        """Test paying a sub-transaction for a different user."""
        # Arrange
        sub_transaction_id = 2
        user_id = 2

        mock_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_sub_transaction.is_paying.return_value = True

        self.mock_sub_transaction_repository.get.return_value = mock_sub_transaction

        # Act
        result = self.use_case.execute(sub_transaction_id, user_id)

        # Assert
        self.mock_sub_transaction_repository.get.assert_called_once_with(sub_transaction_id, user_id)
        mock_sub_transaction.pay.assert_called_once()
        self.assertEqual(result, {"message": "success"})

