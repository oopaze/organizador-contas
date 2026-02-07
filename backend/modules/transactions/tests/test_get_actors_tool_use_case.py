from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.tools.get_actors import GetActorsToolUseCase
from modules.transactions.domains import ActorDomain, SubTransactionDomain


class TestGetActorsToolUseCase(TestCase):
    """Test GetActorsToolUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_actor_repository = Mock()
        self.mock_actor_serializer = Mock()
        self.mock_sub_transaction_repository = Mock()
        self.user_id = 1

        self.use_case = GetActorsToolUseCase(
            actor_repository=self.mock_actor_repository,
            actor_serializer=self.mock_actor_serializer,
            sub_transaction_repository=self.mock_sub_transaction_repository,
            user_id=self.user_id,
        )

    def test_get_actors_with_sub_transactions_in_period(self):
        """Test getting actors with sub-transactions in a specific period."""
        # Arrange
        due_date_start = "2026-03-01"
        due_date_end = "2026-03-31"

        mock_actor1 = Mock(spec=ActorDomain)
        mock_actor1.id = 1
        mock_actor2 = Mock(spec=ActorDomain)
        mock_actor2.id = 2

        mock_sub_transaction1 = Mock(spec=SubTransactionDomain)
        mock_sub_transaction1.actor = Mock()
        mock_sub_transaction1.actor.id = 1

        mock_sub_transaction2 = Mock(spec=SubTransactionDomain)
        mock_sub_transaction2.actor = Mock()
        mock_sub_transaction2.actor.id = 1

        self.mock_actor_repository.get_all.return_value = [mock_actor1, mock_actor2]
        self.mock_sub_transaction_repository.filter_by_actor_ids.return_value = [
            mock_sub_transaction1,
            mock_sub_transaction2,
        ]
        self.mock_actor_serializer.serialize_many_for_tool.return_value = "Actor 1: $100.00"

        # Act
        result = self.use_case.execute(due_date_start, due_date_end)

        # Assert
        self.mock_actor_repository.get_all.assert_called_once_with(self.user_id)
        self.mock_sub_transaction_repository.filter_by_actor_ids.assert_called_once()
        
        # Verify filters were passed correctly
        call_args = self.mock_sub_transaction_repository.filter_by_actor_ids.call_args
        self.assertEqual(call_args[0][0], [1, 2])  # actor IDs
        filters = call_args[0][1]
        self.assertEqual(filters["transaction__due_date__gte"], due_date_start)
        self.assertEqual(filters["transaction__due_date__lte"], due_date_end)
        self.assertEqual(filters["transaction__user_id"], self.user_id)

        # Only actor1 should have sub-transactions set
        mock_actor1.set_sub_transactions.assert_called_once()
        self.assertEqual(result, "Actor 1: $100.00")

    def test_get_actors_filters_actors_without_sub_transactions(self):
        """Test that actors without sub-transactions in period are filtered out."""
        # Arrange
        due_date_start = "2026-03-01"
        due_date_end = "2026-03-31"

        mock_actor1 = Mock(spec=ActorDomain)
        mock_actor1.id = 1
        mock_actor2 = Mock(spec=ActorDomain)
        mock_actor2.id = 2

        # No sub-transactions for any actor
        self.mock_actor_repository.get_all.return_value = [mock_actor1, mock_actor2]
        self.mock_sub_transaction_repository.filter_by_actor_ids.return_value = []
        self.mock_actor_serializer.serialize_many_for_tool.return_value = ""

        # Act
        result = self.use_case.execute(due_date_start, due_date_end)

        # Assert
        self.mock_actor_repository.get_all.assert_called_once_with(self.user_id)
        # No actors should be serialized since none have sub-transactions
        self.mock_actor_serializer.serialize_many_for_tool.assert_called_once_with([])
        self.assertEqual(result, "")

    def test_get_actors_groups_sub_transactions_by_actor(self):
        """Test that sub-transactions are correctly grouped by actor."""
        # Arrange
        due_date_start = "2026-03-01"
        due_date_end = "2026-03-31"

        mock_actor1 = Mock(spec=ActorDomain)
        mock_actor1.id = 1
        mock_actor2 = Mock(spec=ActorDomain)
        mock_actor2.id = 2

        # Actor 1 has 2 sub-transactions, Actor 2 has 1
        mock_sub_transaction1 = Mock(spec=SubTransactionDomain)
        mock_sub_transaction1.actor = Mock()
        mock_sub_transaction1.actor.id = 1

        mock_sub_transaction2 = Mock(spec=SubTransactionDomain)
        mock_sub_transaction2.actor = Mock()
        mock_sub_transaction2.actor.id = 1

        mock_sub_transaction3 = Mock(spec=SubTransactionDomain)
        mock_sub_transaction3.actor = Mock()
        mock_sub_transaction3.actor.id = 2

        self.mock_actor_repository.get_all.return_value = [mock_actor1, mock_actor2]
        self.mock_sub_transaction_repository.filter_by_actor_ids.return_value = [
            mock_sub_transaction1,
            mock_sub_transaction2,
            mock_sub_transaction3,
        ]
        self.mock_actor_serializer.serialize_many_for_tool.return_value = "Actors data"

        # Act
        result = self.use_case.execute(due_date_start, due_date_end)

        # Assert
        # Actor 1 should have 2 sub-transactions
        actor1_call = mock_actor1.set_sub_transactions.call_args[0][0]
        self.assertEqual(len(actor1_call), 2)
        
        # Actor 2 should have 1 sub-transaction
        actor2_call = mock_actor2.set_sub_transactions.call_args[0][0]
        self.assertEqual(len(actor2_call), 1)

    def test_get_actors_method_alias(self):
        """Test that get_actors method works as an alias to execute."""
        # Arrange
        due_date_start = "2026-03-01"
        due_date_end = "2026-03-31"

        self.mock_actor_repository.get_all.return_value = []
        self.mock_sub_transaction_repository.filter_by_actor_ids.return_value = []
        self.mock_actor_serializer.serialize_many_for_tool.return_value = ""

        # Act
        result = self.use_case.get_actors(due_date_start, due_date_end)

        # Assert
        self.mock_actor_repository.get_all.assert_called_once_with(self.user_id)
        self.assertEqual(result, "")

