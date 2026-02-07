from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.actor.list import ListActorsUseCase
from modules.transactions.domains import ActorDomain, SubTransactionDomain


class TestListActorsUseCase(TestCase):
    """Test ListActorsUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_actor_repository = Mock()
        self.mock_actor_serializer = Mock()
        self.mock_sub_transaction_repository = Mock()
        self.mock_sub_transaction_serializer = Mock()

        self.use_case = ListActorsUseCase(
            actor_repository=self.mock_actor_repository,
            actor_serializer=self.mock_actor_serializer,
            sub_transaction_repository=self.mock_sub_transaction_repository,
            sub_transaction_serializer=self.mock_sub_transaction_serializer,
        )

    def test_list_actors_with_sub_transactions(self):
        """Test listing actors with their sub-transactions."""
        # Arrange
        user_id = 1
        due_date = "2026-03"

        mock_actor1 = Mock(spec=ActorDomain)
        mock_actor1.id = 1
        mock_actor2 = Mock(spec=ActorDomain)
        mock_actor2.id = 2

        mock_sub_transaction1 = Mock(spec=SubTransactionDomain)
        mock_sub_transaction1.actor = Mock()
        mock_sub_transaction1.actor.id = 1

        mock_sub_transaction2 = Mock(spec=SubTransactionDomain)
        mock_sub_transaction2.actor = Mock()
        mock_sub_transaction2.actor.id = 2

        self.mock_actor_repository.get_all.return_value = [mock_actor1, mock_actor2]
        self.mock_sub_transaction_repository.get_all.return_value = [mock_sub_transaction1, mock_sub_transaction2]
        self.mock_actor_serializer.serialize.side_effect = [
            {"id": 1, "name": "Actor 1"},
            {"id": 2, "name": "Actor 2"},
        ]

        # Act
        result = self.use_case.execute(user_id, due_date)

        # Assert
        self.mock_actor_repository.get_all.assert_called_once_with(user_id)
        self.mock_sub_transaction_repository.get_all.assert_called_once_with(user_id, due_date)
        self.assertEqual(len(result), 2)
        mock_actor1.set_sub_transactions.assert_called_once()
        mock_actor2.set_sub_transactions.assert_called_once()

    def test_list_actors_without_due_date(self):
        """Test listing actors without due date filter."""
        # Arrange
        user_id = 1

        mock_actor = Mock(spec=ActorDomain)
        mock_actor.id = 1

        self.mock_actor_repository.get_all.return_value = [mock_actor]
        self.mock_sub_transaction_repository.get_all.return_value = []
        self.mock_actor_serializer.serialize.return_value = {"id": 1, "name": "Actor 1"}

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.mock_actor_repository.get_all.assert_called_once_with(user_id)
        self.mock_sub_transaction_repository.get_all.assert_called_once_with(user_id, None)
        self.assertEqual(len(result), 1)

    def test_separe_sub_transactions_by_actor(self):
        """Test separating sub-transactions by actor."""
        # Arrange
        mock_sub_transaction1 = Mock(spec=SubTransactionDomain)
        mock_sub_transaction1.actor = Mock()
        mock_sub_transaction1.actor.id = 1

        mock_sub_transaction2 = Mock(spec=SubTransactionDomain)
        mock_sub_transaction2.actor = Mock()
        mock_sub_transaction2.actor.id = 1

        mock_sub_transaction3 = Mock(spec=SubTransactionDomain)
        mock_sub_transaction3.actor = Mock()
        mock_sub_transaction3.actor.id = 2

        # Sub-transaction without actor
        mock_sub_transaction4 = Mock(spec=SubTransactionDomain)
        mock_sub_transaction4.actor = None

        sub_transactions = [mock_sub_transaction1, mock_sub_transaction2, mock_sub_transaction3, mock_sub_transaction4]

        # Act
        result = self.use_case.separe_sub_transactions_by_actor(sub_transactions)

        # Assert
        self.assertEqual(len(result), 2)  # Only 2 actors
        self.assertEqual(len(result[1]), 2)  # Actor 1 has 2 sub-transactions
        self.assertEqual(len(result[2]), 1)  # Actor 2 has 1 sub-transaction

    def test_list_actors_filters_actors_without_sub_transactions(self):
        """Test that actors without sub-transactions in the period are not included."""
        # Arrange
        user_id = 1
        due_date = "2026-03"

        mock_actor1 = Mock(spec=ActorDomain)
        mock_actor1.id = 1
        mock_actor2 = Mock(spec=ActorDomain)
        mock_actor2.id = 2

        # Only actor 1 has sub-transactions
        mock_sub_transaction = Mock(spec=SubTransactionDomain)
        mock_sub_transaction.actor = Mock()
        mock_sub_transaction.actor.id = 1

        self.mock_actor_repository.get_all.return_value = [mock_actor1, mock_actor2]
        self.mock_sub_transaction_repository.get_all.return_value = [mock_sub_transaction]
        self.mock_actor_serializer.serialize.side_effect = [
            {"id": 1, "name": "Actor 1"},
            {"id": 2, "name": "Actor 2"}
        ]

        # Act
        result = self.use_case.execute(user_id, due_date)

        # Assert
        # Both actors should be in the result, but only actor 1 has sub-transactions
        self.assertEqual(len(result), 2)
        mock_actor1.set_sub_transactions.assert_called_once_with([mock_sub_transaction])
        mock_actor2.set_sub_transactions.assert_called_once_with([])

