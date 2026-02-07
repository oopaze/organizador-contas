from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.actor.delete import DeleteActorUseCase


class TestDeleteActorUseCase(TestCase):
    """Test DeleteActorUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_actor_repository = Mock()

        self.use_case = DeleteActorUseCase(
            actor_repository=self.mock_actor_repository,
        )

    def test_delete_actor(self):
        """Test deleting an actor."""
        # Arrange
        actor_id = 1
        user_id = 1

        # Act
        self.use_case.execute(actor_id, user_id)

        # Assert
        self.mock_actor_repository.delete.assert_called_once_with(actor_id, user_id)

    def test_delete_actor_different_user(self):
        """Test deleting an actor for a different user."""
        # Arrange
        actor_id = 2
        user_id = 2

        # Act
        self.use_case.execute(actor_id, user_id)

        # Assert
        self.mock_actor_repository.delete.assert_called_once_with(actor_id, user_id)

