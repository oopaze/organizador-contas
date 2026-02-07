from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.transaction.delete import DeleteTransactionUseCase
from modules.transactions.domains import TransactionDomain, SubTransactionDomain


class TestDeleteTransactionUseCase(TestCase):
    """Test DeleteTransactionUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_transaction_repository = Mock()
        self.mock_sub_transaction_repository = Mock()

        self.use_case = DeleteTransactionUseCase(
            transaction_repository=self.mock_transaction_repository,
            sub_transaction_repository=self.mock_sub_transaction_repository,
        )

    def test_delete_simple_transaction(self):
        """Test deleting a simple non-recurrent transaction."""
        # Arrange
        transaction_id = 1
        user_id = 1

        mock_transaction = TransactionDomain(
            id=transaction_id,
            due_date="2026-03-15",
            total_amount=150.00,
            transaction_identifier="Bill to Delete",
            transaction_type="outgoing",
            user_id=user_id,
            is_recurrent=False,
        )

        mock_sub_transactions = [
            SubTransactionDomain(
                id=1,
                date="2026-03-15",
                description="Bill to Delete",
                amount=150.00,
                installment_info="1/1",
            )
        ]

        self.mock_transaction_repository.get.return_value = mock_transaction
        self.mock_transaction_repository.get_children_transactions.return_value = []
        self.mock_sub_transaction_repository.get_all_by_transaction_id.return_value = mock_sub_transactions

        # Act
        self.use_case.execute(transaction_id, user_id)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(transaction_id, user_id)
        self.mock_transaction_repository.delete.assert_called_once_with(transaction_id, user_id)
        self.mock_sub_transaction_repository.get_all_by_transaction_id.assert_called_once_with(transaction_id, user_id)
        self.mock_sub_transaction_repository.delete_many.assert_called_once_with(mock_sub_transactions)

    def test_delete_recurrent_transaction_with_children(self):
        """Test deleting a recurrent transaction deletes all children."""
        # Arrange
        transaction_id = 1
        user_id = 1

        mock_transaction = TransactionDomain(
            id=transaction_id,
            due_date="2026-03-15",
            total_amount=100.00,
            transaction_identifier="Subscription to Delete",
            transaction_type="outgoing",
            user_id=user_id,
            is_recurrent=True,
            recurrence_count=3,
        )

        # Mock child transactions
        mock_children = [
            TransactionDomain(id=2, due_date="2026-04-15", user_id=user_id, is_recurrent=True),
            TransactionDomain(id=3, due_date="2026-05-15", user_id=user_id, is_recurrent=True),
        ]

        # Mock sub-transactions for each transaction
        mock_sub_transactions_main = [Mock(spec=SubTransactionDomain, id=1, description="Main", amount=100.00)]
        mock_sub_transactions_child1 = [Mock(spec=SubTransactionDomain, id=2, description="Child 1", amount=100.00)]
        mock_sub_transactions_child2 = [Mock(spec=SubTransactionDomain, id=3, description="Child 2", amount=100.00)]

        self.mock_transaction_repository.get.return_value = mock_transaction
        self.mock_transaction_repository.get_children_transactions.return_value = mock_children
        self.mock_sub_transaction_repository.get_all_by_transaction_id.side_effect = [
            mock_sub_transactions_child1,  # First child
            mock_sub_transactions_child2,  # Second child
            mock_sub_transactions_main,    # Main transaction
        ]

        # Act
        self.use_case.execute(transaction_id, user_id)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(transaction_id, user_id)
        self.mock_transaction_repository.get_children_transactions.assert_called_once_with(transaction_id, user_id)
        
        # Should delete all children + main transaction (3 total)
        self.assertEqual(self.mock_transaction_repository.delete.call_count, 3)
        self.assertEqual(self.mock_sub_transaction_repository.delete_many.call_count, 3)

    def test_delete_transaction_without_sub_transactions(self):
        """Test deleting a transaction that has no sub-transactions."""
        # Arrange
        transaction_id = 1
        user_id = 1

        mock_transaction = TransactionDomain(
            id=transaction_id,
            due_date="2026-03-15",
            total_amount=150.00,
            transaction_identifier="Bill without subs",
            transaction_type="outgoing",
            user_id=user_id,
            is_recurrent=False,
        )

        self.mock_transaction_repository.get.return_value = mock_transaction
        self.mock_transaction_repository.get_children_transactions.return_value = []
        self.mock_sub_transaction_repository.get_all_by_transaction_id.return_value = []

        # Act
        self.use_case.execute(transaction_id, user_id)

        # Assert
        self.mock_transaction_repository.get.assert_called_once_with(transaction_id, user_id)
        self.mock_transaction_repository.delete.assert_called_once_with(transaction_id, user_id)
        self.mock_sub_transaction_repository.get_all_by_transaction_id.assert_called_once_with(transaction_id, user_id)
        # delete_many should still be called, just with empty list
        self.mock_sub_transaction_repository.delete_many.assert_called_once_with([])

