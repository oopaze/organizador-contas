from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.userdata.use_cases.login import LoginUseCase
from modules.userdata.domains.user import UserDomain


class TestLoginUseCase(SimpleTestCase):
    def setUp(self):
        """Set up test dependencies."""
        self.mock_user_repository = Mock()
        self.mock_jwt_gateway = Mock()
        self.mock_user_serializer = Mock()

        self.use_case = LoginUseCase(
            user_repository=self.mock_user_repository,
            jwt_gateway=self.mock_jwt_gateway,
            user_serializer=self.mock_user_serializer,
        )

    def test_execute_successful_login(self):
        """Test that execute authenticates user and returns tokens."""
        # Arrange
        email = "test@example.com"
        password = "password123"

        mock_user = Mock(spec=UserDomain, id=1, email=email, is_active=True)
        self.mock_user_repository.authenticate.return_value = mock_user
        
        self.mock_jwt_gateway.generate_tokens.return_value = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123",
        }
        
        self.mock_user_serializer.serialize.return_value = {
            "id": 1,
            "email": email,
            "is_active": True,
        }

        # Act
        result = self.use_case.execute(email, password)

        # Assert
        self.mock_user_repository.authenticate.assert_called_once_with(email, password)
        self.mock_jwt_gateway.generate_tokens.assert_called_once_with(1, email)
        self.mock_user_serializer.serialize.assert_called_once_with(mock_user)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["access_token"], "access_token_123")
        self.assertEqual(result["refresh_token"], "refresh_token_123")
        self.assertEqual(result["user"]["id"], 1)

    def test_execute_returns_none_with_invalid_credentials(self):
        """Test that execute returns None when credentials are invalid."""
        # Arrange
        email = "test@example.com"
        password = "wrong_password"

        self.mock_user_repository.authenticate.return_value = None

        # Act
        result = self.use_case.execute(email, password)

        # Assert
        self.mock_user_repository.authenticate.assert_called_once_with(email, password)
        self.mock_jwt_gateway.generate_tokens.assert_not_called()
        self.mock_user_serializer.serialize.assert_not_called()
        self.assertIsNone(result)

    def test_execute_returns_none_when_user_is_inactive(self):
        """Test that execute returns None when user is inactive."""
        # Arrange
        email = "test@example.com"
        password = "password123"

        mock_user = Mock(spec=UserDomain, id=1, email=email, is_active=False)
        self.mock_user_repository.authenticate.return_value = mock_user

        # Act
        result = self.use_case.execute(email, password)

        # Assert
        self.mock_user_repository.authenticate.assert_called_once_with(email, password)
        self.mock_jwt_gateway.generate_tokens.assert_not_called()
        self.mock_user_serializer.serialize.assert_not_called()
        self.assertIsNone(result)

    def test_execute_generates_jwt_tokens(self):
        """Test that execute generates JWT tokens for authenticated user."""
        # Arrange
        email = "test@example.com"
        password = "password123"

        mock_user = Mock(spec=UserDomain, id=1, email=email, is_active=True)
        self.mock_user_repository.authenticate.return_value = mock_user
        
        self.mock_jwt_gateway.generate_tokens.return_value = {
            "access_token": "access_123",
            "refresh_token": "refresh_123",
        }
        
        self.mock_user_serializer.serialize.return_value = {"id": 1, "email": email}

        # Act
        result = self.use_case.execute(email, password)

        # Assert
        self.mock_jwt_gateway.generate_tokens.assert_called_once_with(1, email)
        self.assertEqual(result["access_token"], "access_123")
        self.assertEqual(result["refresh_token"], "refresh_123")

    def test_execute_serializes_user_data(self):
        """Test that execute serializes user data correctly."""
        # Arrange
        email = "test@example.com"
        password = "password123"

        mock_user = Mock(spec=UserDomain, id=1, email=email, is_active=True)
        self.mock_user_repository.authenticate.return_value = mock_user
        
        self.mock_jwt_gateway.generate_tokens.return_value = {
            "access_token": "access_123",
            "refresh_token": "refresh_123",
        }
        
        serialized_user = {
            "id": 1,
            "email": email,
            "is_active": True,
            "is_staff": False,
        }
        self.mock_user_serializer.serialize.return_value = serialized_user

        # Act
        result = self.use_case.execute(email, password)

        # Assert
        self.mock_user_serializer.serialize.assert_called_once_with(mock_user)
        self.assertEqual(result["user"], serialized_user)

