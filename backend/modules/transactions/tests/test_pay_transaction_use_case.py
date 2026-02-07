from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.transaction.pay import PayTransactionUseCase
from modules.transactions.domains import TransactionDomain, SubTransactionDomain


class TestPayTransactionUseCase(TestCase):
    """Test PayTransactionUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_transaction_repository = Mock()
        self.mock_sub_transaction_repository = Mock()

        self.use_case = PayTransactionUseCase(
            transaction_repository=self.mock_transaction_repository,
            sub_transaction_repository=self.mock_sub_transaction_repository,
        )

    def test_pay_transaction_marks_as_paid(self):
        """Test paying a transaction marks it as paid."""
        # Arrange
        transaction_id = 1
        user_id = 1

        mock_transaction = Mock(spec=TransactionDomain)
        mock_transaction.is_paying.return_value = True  # Transaction is being paid

        self.mock_transaction_repository.get.return_value = mock_transaction

        # Act
        result = self.use_case.execute(transaction_id, user_id, update_sub_transactions=False)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(transaction_id, user_id)
        mock_transaction.is_paying.assert_called_once()
        mock_transaction.pay.assert_called_once()
        mock_transaction.unpay.assert_not_called()
        self.mock_transaction_repository.update_paid_at.assert_called_once_with(mock_transaction)
        self.assertEqual(result, {"message": "success"})

    def test_unpay_transaction_marks_as_unpaid(self):
        """Test unpaying a transaction marks it as unpaid."""
        # Arrange
        transaction_id = 1
        user_id = 1

        mock_transaction = Mock(spec=TransactionDomain)
        mock_transaction.is_paying.return_value = False  # Transaction is being unpaid

        self.mock_transaction_repository.get.return_value = mock_transaction

        # Act
        result = self.use_case.execute(transaction_id, user_id, update_sub_transactions=False)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(transaction_id, user_id)
        mock_transaction.is_paying.assert_called_once()
        mock_transaction.unpay.assert_called_once()
        mock_transaction.pay.assert_not_called()
        self.mock_transaction_repository.update_paid_at.assert_called_once_with(mock_transaction)
        self.assertEqual(result, {"message": "success"})

    def test_pay_transaction_with_sub_transactions(self):
        """Test paying a transaction also pays all sub-transactions."""
        # Arrange
        transaction_id = 1
        user_id = 1

        mock_transaction = Mock(spec=TransactionDomain)
        mock_transaction.is_paying.return_value = True

        mock_sub_transactions = [
            Mock(spec=SubTransactionDomain),
            Mock(spec=SubTransactionDomain),
        ]

        self.mock_transaction_repository.get.return_value = mock_transaction
        self.mock_sub_transaction_repository.get_all_by_transaction_id.return_value = mock_sub_transactions

        # Act
        result = self.use_case.execute(transaction_id, user_id, update_sub_transactions=True)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(transaction_id, user_id)
        mock_transaction.pay.assert_called_once()
        self.mock_transaction_repository.update_paid_at.assert_called_once_with(mock_transaction)
        
        # Verify sub-transactions were paid
        self.mock_sub_transaction_repository.get_all_by_transaction_id.assert_called_once_with(transaction_id, user_id)
        for sub_transaction in mock_sub_transactions:
            sub_transaction.pay.assert_called_once()
            sub_transaction.unpay.assert_not_called()
        self.assertEqual(self.mock_sub_transaction_repository.update_paid_at.call_count, 2)
        self.assertEqual(result, {"message": "success"})

    def test_unpay_transaction_with_sub_transactions(self):
        """Test unpaying a transaction also unpays all sub-transactions."""
        # Arrange
        transaction_id = 1
        user_id = 1

        mock_transaction = Mock(spec=TransactionDomain)
        mock_transaction.is_paying.return_value = False

        mock_sub_transactions = [
            Mock(spec=SubTransactionDomain),
            Mock(spec=SubTransactionDomain),
        ]

        self.mock_transaction_repository.get.return_value = mock_transaction
        self.mock_sub_transaction_repository.get_all_by_transaction_id.return_value = mock_sub_transactions

        # Act
        result = self.use_case.execute(transaction_id, user_id, update_sub_transactions=True)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(transaction_id, user_id)
        mock_transaction.unpay.assert_called_once()
        self.mock_transaction_repository.update_paid_at.assert_called_once_with(mock_transaction)
        
        # Verify sub-transactions were unpaid
        self.mock_sub_transaction_repository.get_all_by_transaction_id.assert_called_once_with(transaction_id, user_id)
        for sub_transaction in mock_sub_transactions:
            sub_transaction.unpay.assert_called_once()
            sub_transaction.pay.assert_not_called()
        self.assertEqual(self.mock_sub_transaction_repository.update_paid_at.call_count, 2)
        self.assertEqual(result, {"message": "success"})

    def test_pay_transaction_without_updating_sub_transactions(self):
        """Test paying a transaction without updating sub-transactions."""
        # Arrange
        transaction_id = 1
        user_id = 1

        mock_transaction = Mock(spec=TransactionDomain)
        mock_transaction.is_paying.return_value = True

        self.mock_transaction_repository.get.return_value = mock_transaction

        # Act
        result = self.use_case.execute(transaction_id, user_id, update_sub_transactions=False)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(transaction_id, user_id)
        mock_transaction.pay.assert_called_once()
        self.mock_transaction_repository.update_paid_at.assert_called_once_with(mock_transaction)
        
        # Verify sub-transactions were NOT queried or updated
        self.mock_sub_transaction_repository.get_all_by_transaction_id.assert_not_called()
        self.mock_sub_transaction_repository.update_paid_at.assert_not_called()
        self.assertEqual(result, {"message": "success"})

