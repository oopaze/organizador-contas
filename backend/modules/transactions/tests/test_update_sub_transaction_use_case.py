from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.sub_transaction.update import UpdateSubTransactionUseCase
from modules.transactions.domains import SubTransactionDomain, ActorDomain


class TestUpdateSubTransactionUseCase(TestCase):
    """Test UpdateSubTransactionUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_sub_transaction_repository = Mock()
        self.mock_sub_transaction_serializer = Mock()
        self.mock_actor_repository = Mock()

        self.use_case = UpdateSubTransactionUseCase(
            sub_transaction_repository=self.mock_sub_transaction_repository,
            sub_transaction_serializer=self.mock_sub_transaction_serializer,
            actor_repository=self.mock_actor_repository,
        )

    def test_update_sub_transaction_simple(self):
        """Test updating a sub-transaction without dividing for actor."""
        # Arrange
        sub_transaction_id = 1
        user_id = 1
        data = {
            "description": "Updated description",
            "amount": 75.00,
        }

        mock_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_sub_transaction.amount = 75.00
        updated_mock_sub_transaction = Mock(
            spec=SubTransactionDomain,
            id=sub_transaction_id,
            description="Updated description",
            amount=75.00,
        )

        self.mock_sub_transaction_repository.get.return_value = mock_sub_transaction
        self.mock_sub_transaction_repository.update.return_value = updated_mock_sub_transaction
        self.mock_sub_transaction_serializer.serialize.return_value = {"id": 1, "description": "Updated description"}

        # Act
        result = self.use_case.execute(sub_transaction_id, data, user_id)

        # Assert
        self.mock_sub_transaction_repository.get.assert_called_once_with(sub_transaction_id, user_id)
        self.mock_sub_transaction_repository.update.assert_called_once_with(mock_sub_transaction)
        self.assertEqual(result, {"id": 1, "description": "Updated description"})

    def test_update_sub_transaction_with_actor(self):
        """Test updating a sub-transaction with an actor."""
        # Arrange
        sub_transaction_id = 1
        user_id = 1
        data = {
            "actor": 1,
            "description": "Shared expense",
            "amount": 100.00,
        }

        mock_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_sub_transaction.amount = 100.00
        mock_actor = Mock(spec=ActorDomain)
        mock_actor.id = 1
        mock_actor.name = "John Doe"

        self.mock_sub_transaction_repository.get.return_value = mock_sub_transaction
        self.mock_actor_repository.get.return_value = mock_actor
        self.mock_sub_transaction_repository.update.return_value = mock_sub_transaction
        self.mock_sub_transaction_serializer.serialize.return_value = {"id": 1, "description": "Shared expense"}

        # Act
        result = self.use_case.execute(sub_transaction_id, data, user_id)

        # Assert
        self.mock_sub_transaction_repository.get.assert_called_once_with(sub_transaction_id, user_id)
        self.mock_actor_repository.get.assert_called_once_with(1, user_id)  # data["actor"] is the actor ID (1)
        mock_sub_transaction.update.assert_called_once()
        self.assertEqual(result, {"id": 1, "description": "Shared expense"})

    def test_update_sub_transaction_divide_for_actor(self):
        """Test updating a sub-transaction and dividing amount for actor."""
        # Arrange
        sub_transaction_id = 1
        user_id = 1
        data = {
            "actor": 1,
            "should_divide_for_actor": True,
            "actor_amount": 30.00,
        }

        mock_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_sub_transaction.id = 1
        mock_sub_transaction.amount = 100.00
        mock_sub_transaction.user_provided_description = "Original"

        mock_actor = Mock(spec=ActorDomain)
        mock_actor.id = 1
        mock_actor.name = "John Doe"

        mock_duplicated_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_duplicated_sub_transaction.amount = 30.00

        self.mock_sub_transaction_repository.get.return_value = mock_sub_transaction
        self.mock_actor_repository.get.return_value = mock_actor
        self.mock_sub_transaction_repository.duplicate.return_value = mock_duplicated_sub_transaction
        self.mock_sub_transaction_repository.update.return_value = mock_sub_transaction
        self.mock_sub_transaction_serializer.serialize.return_value = {"id": 1}

        # Act
        result = self.use_case.execute(sub_transaction_id, data, user_id)

        # Assert
        self.mock_sub_transaction_repository.get.assert_called_once_with(sub_transaction_id, user_id)
        self.mock_actor_repository.get.assert_called_once_with(1, user_id)  # data["actor"] is the actor ID (1)
        # Should duplicate the sub-transaction for the actor
        self.mock_sub_transaction_repository.duplicate.assert_called_once()
        # Original sub-transaction should be updated with reduced amount
        mock_sub_transaction.update.assert_called()

    def test_give_part_to_actor(self):
        """Test the give_part_to_actor method."""
        # Arrange
        mock_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_sub_transaction.id = 1
        mock_sub_transaction.amount = 100.00
        mock_sub_transaction.user_provided_description = "Shared bill"

        mock_actor = Mock(spec=ActorDomain)
        mock_actor.id = 1
        mock_actor.name = "Jane"

        data = {"actor_amount": 40.00}

        mock_duplicated = Mock(spec=SubTransactionDomain)
        mock_duplicated.amount = 40.00

        self.mock_sub_transaction_repository.duplicate.return_value = mock_duplicated

        # Act
        result = self.use_case.give_part_to_actor(mock_sub_transaction, data, mock_actor)

        # Assert
        self.mock_sub_transaction_repository.duplicate.assert_called_once()
        # Verify the duplicate was called with correct parameters
        call_args = self.mock_sub_transaction_repository.duplicate.call_args
        self.assertEqual(call_args[0][0], 1)  # sub_transaction_id
        self.assertEqual(call_args[0][1]["amount"], 40.00)
        self.assertEqual(call_args[0][1]["actor_id"], 1)
        # Original sub-transaction should be updated
        mock_sub_transaction.update.assert_called_once()

