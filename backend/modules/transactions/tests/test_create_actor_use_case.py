from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.actor.create import CreateActorUseCase
from modules.transactions.domains import ActorDomain


class TestCreateActorUseCase(TestCase):
    """Test CreateActorUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_actor_repository = Mock()
        self.mock_actor_serializer = Mock()
        self.mock_actor_factory = Mock()

        self.use_case = CreateActorUseCase(
            actor_repository=self.mock_actor_repository,
            actor_serializer=self.mock_actor_serializer,
            actor_factory=self.mock_actor_factory,
        )

    def test_create_actor(self):
        """Test creating an actor."""
        # Arrange
        name = "John Doe"
        user_id = 1

        mock_actor = ActorDomain(
            id=1,
            name=name,
            user_id=user_id,
        )

        self.mock_actor_factory.build.return_value = mock_actor
        self.mock_actor_repository.create.return_value = mock_actor
        self.mock_actor_serializer.serialize.return_value = {"id": 1, "name": name}

        # Act
        result = self.use_case.execute(name, user_id)

        # Assert
        self.mock_actor_factory.build.assert_called_once_with(name, user_id)
        self.mock_actor_repository.create.assert_called_once_with(mock_actor)
        self.mock_actor_serializer.serialize.assert_called_once_with(mock_actor)
        self.assertEqual(result, {"id": 1, "name": name})

    def test_create_actor_with_different_user(self):
        """Test creating an actor for a different user."""
        # Arrange
        name = "Jane Smith"
        user_id = 2

        mock_actor = ActorDomain(
            id=2,
            name=name,
            user_id=user_id,
        )

        self.mock_actor_factory.build.return_value = mock_actor
        self.mock_actor_repository.create.return_value = mock_actor
        self.mock_actor_serializer.serialize.return_value = {"id": 2, "name": name}

        # Act
        result = self.use_case.execute(name, user_id)

        # Assert
        self.mock_actor_factory.build.assert_called_once_with(name, user_id)
        self.mock_actor_repository.create.assert_called_once_with(mock_actor)
        self.assertEqual(result["name"], name)

