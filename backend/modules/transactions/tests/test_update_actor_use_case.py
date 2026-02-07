from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.actor.update import UpdateActorUseCase
from modules.transactions.domains import ActorDomain


class TestUpdateActorUseCase(TestCase):
    """Test UpdateActorUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_actor_repository = Mock()
        self.mock_actor_serializer = Mock()

        self.use_case = UpdateActorUseCase(
            actor_repository=self.mock_actor_repository,
            actor_serializer=self.mock_actor_serializer,
        )

    def test_update_actor(self):
        """Test updating an actor's name."""
        # Arrange
        actor_id = 1
        new_name = "Updated Name"
        user_id = 1

        mock_actor = Mock(spec=ActorDomain)
        updated_mock_actor = ActorDomain(
            id=actor_id,
            name=new_name,
            user_id=user_id,
        )

        self.mock_actor_repository.get.return_value = mock_actor
        self.mock_actor_repository.update.return_value = updated_mock_actor
        self.mock_actor_serializer.serialize.return_value = {"id": actor_id, "name": new_name}

        # Act
        result = self.use_case.execute(actor_id, new_name, user_id)

        # Assert
        self.mock_actor_repository.get.assert_called_once_with(actor_id, user_id)
        mock_actor.update.assert_called_once_with(new_name)
        self.mock_actor_repository.update.assert_called_once_with(mock_actor)
        self.mock_actor_serializer.serialize.assert_called_once_with(updated_mock_actor)
        self.assertEqual(result, {"id": actor_id, "name": new_name})

    def test_update_actor_different_user(self):
        """Test updating an actor for a different user."""
        # Arrange
        actor_id = 2
        new_name = "Another Name"
        user_id = 2

        mock_actor = Mock(spec=ActorDomain)
        updated_mock_actor = ActorDomain(
            id=actor_id,
            name=new_name,
            user_id=user_id,
        )

        self.mock_actor_repository.get.return_value = mock_actor
        self.mock_actor_repository.update.return_value = updated_mock_actor
        self.mock_actor_serializer.serialize.return_value = {"id": actor_id, "name": new_name}

        # Act
        result = self.use_case.execute(actor_id, new_name, user_id)

        # Assert
        self.mock_actor_repository.get.assert_called_once_with(actor_id, user_id)
        mock_actor.update.assert_called_once_with(new_name)
        self.assertEqual(result["name"], new_name)

