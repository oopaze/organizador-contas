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
        mock_sub_transaction.actor = None
        mock_sub_transaction.actor_id = None
        mock_sub_transaction.user_provided_description = "Original"

        mock_actor = Mock(spec=ActorDomain)
        mock_actor.id = 1
        mock_actor.name = "John Doe"

        mock_duplicated_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_duplicated_sub_transaction.amount = 30.00
        mock_duplicated_sub_transaction.actor = mock_actor
        mock_duplicated_sub_transaction.actor_id = mock_actor.id

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
        mock_sub_transaction.actor = None
        mock_sub_transaction.actor_id = None
        mock_sub_transaction.user_provided_description = "Shared bill"

        mock_actor = Mock(spec=ActorDomain)
        mock_actor.id = 1
        mock_actor.name = "Jane"

        data = {"actor_amount": 40.00}

        mock_duplicated = Mock(spec=SubTransactionDomain)
        mock_duplicated.amount = 40.00
        mock_duplicated.actor = mock_actor
        mock_duplicated.actor_id = mock_actor.id

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

    def test_divide_for_actor_preserves_original_actor_and_creates_new_for_specified_actor(self):
        """
        Test that when dividing a sub-transaction for an actor:
        - The ORIGINAL sub-transaction keeps its current actor (if any) and amount is reduced
        - A NEW sub-transaction is created with the specified actor and the divided amount

        Scenario 1: Original has NO actor (belongs to user)
        - User has a $100 bill (actor=None) and wants to split $40 to John
        Expected:
        - Original: amount=$60, actor=None (stays with user)
        - New: amount=$40, actor=John

        Scenario 2: Original has an actor (e.g., Mary)
        - Mary's $100 bill (actor=Mary) and user wants to split $40 to John
        Expected:
        - Original: amount=$60, actor=Mary (keeps Mary)
        - New: amount=$40, actor=John
        """
        # Arrange - Scenario 1: Original has NO actor
        sub_transaction_id = 1
        user_id = 1
        original_amount = 100.00
        actor_amount = 40.00
        expected_remaining_amount = 60.00

        data = {
            "actor": 2,  # John's ID
            "should_divide_for_actor": True,
            "actor_amount": actor_amount,
        }

        # Mock the original sub-transaction (belongs to current user, no actor)
        mock_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_sub_transaction.id = sub_transaction_id
        mock_sub_transaction.amount = original_amount
        mock_sub_transaction.actor = None  # Originally belongs to user
        mock_sub_transaction.actor_id = None
        mock_sub_transaction.user_provided_description = "Shared bill"

        # Configure update method to actually update the mock's attributes
        def update_mock(data):
            if "amount" in data:
                mock_sub_transaction.amount = data["amount"]
            if "actor" in data:
                mock_sub_transaction.actor = data["actor"]
            if "user_provided_description" in data:
                mock_sub_transaction.user_provided_description = data["user_provided_description"]

        mock_sub_transaction.update.side_effect = update_mock

        # Mock the actor (John)
        mock_actor_john = Mock(spec=ActorDomain)
        mock_actor_john.id = 2
        mock_actor_john.name = "John"

        # Mock the duplicated sub-transaction (will be assigned to John)
        mock_duplicated_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_duplicated_sub_transaction.amount = actor_amount

        # Setup repository mocks
        self.mock_sub_transaction_repository.get.return_value = mock_sub_transaction
        self.mock_actor_repository.get.return_value = mock_actor_john
        self.mock_sub_transaction_repository.duplicate.return_value = mock_duplicated_sub_transaction
        self.mock_sub_transaction_repository.update.return_value = mock_sub_transaction
        self.mock_sub_transaction_serializer.serialize.return_value = {
            "id": sub_transaction_id,
            "amount": expected_remaining_amount,
            "actor": None,
        }

        # Act
        result = self.use_case.execute(sub_transaction_id, data, user_id)

        # Assert
        # 1. Verify the duplicate was created with John as actor
        self.mock_sub_transaction_repository.duplicate.assert_called_once()
        duplicate_call_args = self.mock_sub_transaction_repository.duplicate.call_args[0]
        duplicate_call_data = duplicate_call_args[1]
        self.assertEqual(duplicate_call_data["amount"], actor_amount)
        self.assertEqual(duplicate_call_data["actor_id"], mock_actor_john.id)
        self.assertIn("Parte de John", duplicate_call_data["user_provided_description"])

        # 2. Verify the original sub-transaction update was called twice:
        #    - First in give_part_to_actor (reduces amount)
        #    - Second in execute (final update with data)
        self.assertEqual(mock_sub_transaction.update.call_count, 2)

        # 3. CRITICAL: Verify the final update preserves the original actor (None in this case)
        final_update_call = mock_sub_transaction.update.call_args_list[-1][0][0]
        self.assertIn("actor", final_update_call)
        self.assertIsNone(final_update_call["actor"],
                         "Original sub-transaction should preserve its actor (None = user)")

    def test_divide_for_actor_when_original_already_has_different_actor(self):
        """
        Test that when dividing a sub-transaction that ALREADY has an actor:
        - The original keeps its EXISTING actor and amount is reduced
        - A new sub-transaction is created with the NEW actor

        Scenario: Mary's $100 bill, user wants to split $40 to John
        Expected:
        - Original: amount=$60, actor=Mary (preserves Mary)
        - New: amount=$40, actor=John
        """
        # Arrange
        sub_transaction_id = 1
        user_id = 1
        original_amount = 100.00
        actor_amount = 40.00

        data = {
            "actor": 2,  # John's ID (new actor to split to)
            "should_divide_for_actor": True,
            "actor_amount": actor_amount,
        }

        # Mock Mary (existing actor on original transaction)
        mock_actor_mary = Mock(spec=ActorDomain)
        mock_actor_mary.id = 1
        mock_actor_mary.name = "Mary"

        # Mock the original sub-transaction (already belongs to Mary)
        mock_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_sub_transaction.id = sub_transaction_id
        mock_sub_transaction.amount = original_amount
        mock_sub_transaction.actor = mock_actor_mary  # Already has Mary as actor
        mock_sub_transaction.actor_id = mock_actor_mary.id
        mock_sub_transaction.user_provided_description = "Mary's expense"

        # Configure update method to actually update the mock's attributes
        def update_mock(data):
            if "amount" in data:
                mock_sub_transaction.amount = data["amount"]
            if "actor" in data:
                mock_sub_transaction.actor = data["actor"]
            if "user_provided_description" in data:
                mock_sub_transaction.user_provided_description = data["user_provided_description"]

        mock_sub_transaction.update.side_effect = update_mock

        # Mock John (new actor to split to)
        mock_actor_john = Mock(spec=ActorDomain)
        mock_actor_john.id = 2
        mock_actor_john.name = "John"

        # Mock the duplicated sub-transaction (will be assigned to John)
        mock_duplicated_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_duplicated_sub_transaction.amount = actor_amount
        mock_duplicated_sub_transaction.actor = mock_actor_john
        mock_duplicated_sub_transaction.actor_id = mock_actor_john.id

        # Setup repository mocks
        self.mock_sub_transaction_repository.get.return_value = mock_sub_transaction
        self.mock_actor_repository.get.return_value = mock_actor_john
        self.mock_sub_transaction_repository.duplicate.return_value = mock_duplicated_sub_transaction
        self.mock_sub_transaction_repository.update.return_value = mock_sub_transaction
        self.mock_sub_transaction_serializer.serialize.return_value = {
            "id": sub_transaction_id,
            "amount": 60.00,
            "actor": {"id": 1, "name": "Mary"},
        }

        # Act
        result = self.use_case.execute(sub_transaction_id, data, user_id)

        # Assert
        # 1. Verify the duplicate was created with John as actor
        self.mock_sub_transaction_repository.duplicate.assert_called_once()
        duplicate_call_data = self.mock_sub_transaction_repository.duplicate.call_args[0][1]
        self.assertEqual(duplicate_call_data["actor_id"], mock_actor_john.id)

        # 2. CRITICAL: Verify the final update preserves Mary as the actor
        final_update_call = mock_sub_transaction.update.call_args_list[-1][0][0]
        self.assertIn("actor", final_update_call)
        self.assertEqual(final_update_call["actor"], mock_actor_mary,
                        "Original sub-transaction should preserve its existing actor (Mary)")

        # 3. Verify amount was reduced
        self.assertIn("amount", final_update_call)
