from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.userdata.use_cases.get_current_user import GetCurrentUserUseCase
from modules.userdata.domains.user import UserDomain


class TestGetCurrentUserUseCase(SimpleTestCase):
    def setUp(self):
        """Set up test dependencies."""
        self.mock_user_repository = Mock()
        self.mock_user_serializer = Mock()

        self.use_case = GetCurrentUserUseCase(
            user_repository=self.mock_user_repository,
            user_serializer=self.mock_user_serializer,
        )

    def test_execute_returns_serialized_user(self):
        """Test that execute returns serialized user data."""
        # Arrange
        user_id = 1

        mock_user = Mock(spec=UserDomain, id=user_id, email="test@example.com")
        self.mock_user_repository.get_by_id.return_value = mock_user
        
        serialized_user = {
            "id": user_id,
            "email": "test@example.com",
            "is_active": True,
        }
        self.mock_user_serializer.serialize.return_value = serialized_user

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.mock_user_repository.get_by_id.assert_called_once_with(user_id)
        self.mock_user_serializer.serialize.assert_called_once_with(mock_user)
        
        self.assertIsNotNone(result)
        self.assertEqual(result, serialized_user)
        self.assertEqual(result["id"], user_id)

    def test_execute_returns_none_when_user_not_found(self):
        """Test that execute returns None when user is not found."""
        # Arrange
        user_id = 999

        self.mock_user_repository.get_by_id.return_value = None

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.mock_user_repository.get_by_id.assert_called_once_with(user_id)
        self.mock_user_serializer.serialize.assert_not_called()
        self.assertIsNone(result)

    def test_execute_with_different_user_ids(self):
        """Test that execute works with different user IDs."""
        # Arrange
        user_id_1 = 1
        user_id_2 = 42

        mock_user_1 = Mock(spec=UserDomain, id=user_id_1, email="user1@example.com")
        mock_user_2 = Mock(spec=UserDomain, id=user_id_2, email="user2@example.com")
        
        self.mock_user_repository.get_by_id.side_effect = [mock_user_1, mock_user_2]
        
        self.mock_user_serializer.serialize.side_effect = [
            {"id": user_id_1, "email": "user1@example.com"},
            {"id": user_id_2, "email": "user2@example.com"},
        ]

        # Act
        result_1 = self.use_case.execute(user_id_1)
        result_2 = self.use_case.execute(user_id_2)

        # Assert
        self.assertEqual(result_1["id"], user_id_1)
        self.assertEqual(result_2["id"], user_id_2)

    def test_execute_serializes_user_correctly(self):
        """Test that execute calls serializer with correct user object."""
        # Arrange
        user_id = 1

        mock_user = Mock(
            spec=UserDomain,
            id=user_id,
            email="test@example.com",
            is_active=True,
            is_staff=False,
        )
        self.mock_user_repository.get_by_id.return_value = mock_user
        
        serialized_user = {
            "id": user_id,
            "email": "test@example.com",
            "is_active": True,
            "is_staff": False,
        }
        self.mock_user_serializer.serialize.return_value = serialized_user

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.mock_user_serializer.serialize.assert_called_once_with(mock_user)
        self.assertEqual(result, serialized_user)

