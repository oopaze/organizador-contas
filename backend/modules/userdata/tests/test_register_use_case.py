from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.userdata.use_cases.register import RegisterUseCase
from modules.userdata.domains.user import UserDomain
from modules.userdata.domains.profile import ProfileDomain


class TestRegisterUseCase(SimpleTestCase):
    def setUp(self):
        """Set up test dependencies."""
        self.mock_jwt_gateway = Mock()
        self.mock_user_repository = Mock()
        self.mock_profile_repository = Mock()
        self.mock_user_serializer = Mock()

        self.use_case = RegisterUseCase(
            jwt_gateway=self.mock_jwt_gateway,
            user_repository=self.mock_user_repository,
            profile_repository=self.mock_profile_repository,
            user_serializer=self.mock_user_serializer,
        )

    def test_execute_creates_user_and_profile(self):
        """Test that execute creates a new user and profile."""
        # Arrange
        email = "test@example.com"
        password = "password123"
        first_name = "John"
        last_name = "Doe"

        self.mock_user_repository.get_by_email.return_value = None
        
        mock_created_user = Mock(spec=UserDomain, id=1, email=email)
        self.mock_user_repository.create.return_value = mock_created_user
        
        mock_profile = Mock(spec=ProfileDomain, id=1, first_name=first_name, last_name=last_name)
        self.mock_profile_repository.create.return_value = mock_profile
        
        mock_user_with_profile = Mock(spec=UserDomain, id=1, email=email, profile=mock_profile)
        self.mock_user_repository.get_by_id.return_value = mock_user_with_profile
        
        self.mock_jwt_gateway.generate_tokens.return_value = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123",
        }
        
        self.mock_user_serializer.serialize.return_value = {
            "id": 1,
            "email": email,
            "profile": {"first_name": first_name, "last_name": last_name},
        }

        # Act
        result = self.use_case.execute(email, password, first_name, last_name)

        # Assert
        self.mock_user_repository.get_by_email.assert_called_once_with(email)
        self.mock_user_repository.create.assert_called_once_with(email, password)
        self.mock_profile_repository.create.assert_called_once_with(mock_created_user, first_name, last_name)
        self.mock_user_repository.get_by_id.assert_called_once_with(1)
        self.mock_jwt_gateway.generate_tokens.assert_called_once_with(1, email)
        self.mock_user_serializer.serialize.assert_called_once_with(mock_user_with_profile)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["access_token"], "access_token_123")
        self.assertEqual(result["refresh_token"], "refresh_token_123")
        self.assertEqual(result["user"]["id"], 1)

    def test_execute_with_minimal_fields(self):
        """Test that execute works with only email and password."""
        # Arrange
        email = "test@example.com"
        password = "password123"

        self.mock_user_repository.get_by_email.return_value = None
        
        mock_created_user = Mock(spec=UserDomain, id=1, email=email)
        self.mock_user_repository.create.return_value = mock_created_user
        
        mock_user_with_profile = Mock(spec=UserDomain, id=1, email=email)
        self.mock_user_repository.get_by_id.return_value = mock_user_with_profile
        
        self.mock_jwt_gateway.generate_tokens.return_value = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123",
        }
        
        self.mock_user_serializer.serialize.return_value = {"id": 1, "email": email}

        # Act
        result = self.use_case.execute(email, password)

        # Assert
        self.mock_profile_repository.create.assert_called_once_with(mock_created_user, "", "")
        self.assertIsNotNone(result)

    def test_execute_returns_none_when_user_exists(self):
        """Test that execute returns None when user already exists."""
        # Arrange
        email = "existing@example.com"
        password = "password123"

        existing_user = Mock(spec=UserDomain, id=1, email=email)
        self.mock_user_repository.get_by_email.return_value = existing_user

        # Act
        result = self.use_case.execute(email, password)

        # Assert
        self.mock_user_repository.get_by_email.assert_called_once_with(email)
        self.mock_user_repository.create.assert_not_called()
        self.mock_profile_repository.create.assert_not_called()
        self.mock_jwt_gateway.generate_tokens.assert_not_called()
        self.assertIsNone(result)

    def test_execute_generates_jwt_tokens(self):
        """Test that execute generates JWT tokens for new user."""
        # Arrange
        email = "test@example.com"
        password = "password123"

        self.mock_user_repository.get_by_email.return_value = None
        
        mock_created_user = Mock(spec=UserDomain, id=1, email=email)
        self.mock_user_repository.create.return_value = mock_created_user
        
        mock_user_with_profile = Mock(spec=UserDomain, id=1, email=email)
        self.mock_user_repository.get_by_id.return_value = mock_user_with_profile
        
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

