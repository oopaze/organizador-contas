from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.userdata.use_cases.refresh_token import RefreshTokenUseCase
from modules.userdata.domains.user import UserDomain


class TestRefreshTokenUseCase(SimpleTestCase):
    def setUp(self):
        """Set up test dependencies."""
        self.mock_user_repository = Mock()
        self.mock_jwt_gateway = Mock()

        self.use_case = RefreshTokenUseCase(
            user_repository=self.mock_user_repository,
            jwt_gateway=self.mock_jwt_gateway,
        )

    def test_execute_successful_token_refresh(self):
        """Test that execute refreshes tokens successfully."""
        # Arrange
        refresh_token = "valid_refresh_token"
        user_id = 1
        email = "test@example.com"

        payload = {"user_id": user_id, "email": email, "type": "refresh"}
        self.mock_jwt_gateway.validate_refresh_token.return_value = payload
        
        mock_user = Mock(spec=UserDomain, id=user_id, email=email)
        self.mock_user_repository.get_by_id.return_value = mock_user
        
        new_tokens = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
        }
        self.mock_jwt_gateway.generate_tokens.return_value = new_tokens

        # Act
        result = self.use_case.execute(refresh_token)

        # Assert
        self.mock_jwt_gateway.validate_refresh_token.assert_called_once_with(refresh_token)
        self.mock_user_repository.get_by_id.assert_called_once_with(user_id)
        self.mock_jwt_gateway.generate_tokens.assert_called_once_with(user_id, email)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["access_token"], "new_access_token")
        self.assertEqual(result["refresh_token"], "new_refresh_token")

    def test_execute_returns_none_with_invalid_token(self):
        """Test that execute returns None when refresh token is invalid."""
        # Arrange
        refresh_token = "invalid_refresh_token"

        self.mock_jwt_gateway.validate_refresh_token.return_value = None

        # Act
        result = self.use_case.execute(refresh_token)

        # Assert
        self.mock_jwt_gateway.validate_refresh_token.assert_called_once_with(refresh_token)
        self.mock_user_repository.get_by_id.assert_not_called()
        self.mock_jwt_gateway.generate_tokens.assert_not_called()
        self.assertIsNone(result)

    def test_execute_returns_none_when_user_not_found(self):
        """Test that execute returns None when user is not found."""
        # Arrange
        refresh_token = "valid_refresh_token"
        user_id = 999

        payload = {"user_id": user_id, "email": "test@example.com", "type": "refresh"}
        self.mock_jwt_gateway.validate_refresh_token.return_value = payload
        
        self.mock_user_repository.get_by_id.return_value = None

        # Act
        result = self.use_case.execute(refresh_token)

        # Assert
        self.mock_jwt_gateway.validate_refresh_token.assert_called_once_with(refresh_token)
        self.mock_user_repository.get_by_id.assert_called_once_with(user_id)
        self.mock_jwt_gateway.generate_tokens.assert_not_called()
        self.assertIsNone(result)

    def test_execute_validates_token_before_generating_new_tokens(self):
        """Test that execute validates token before generating new ones."""
        # Arrange
        refresh_token = "valid_refresh_token"
        user_id = 1
        email = "test@example.com"

        payload = {"user_id": user_id, "email": email, "type": "refresh"}
        self.mock_jwt_gateway.validate_refresh_token.return_value = payload
        
        mock_user = Mock(spec=UserDomain, id=user_id, email=email)
        self.mock_user_repository.get_by_id.return_value = mock_user
        
        new_tokens = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
        }
        self.mock_jwt_gateway.generate_tokens.return_value = new_tokens

        # Act
        result = self.use_case.execute(refresh_token)

        # Assert
        # Verify the order of calls
        call_order = []
        
        def track_validate_call(*args, **kwargs):
            call_order.append("validate")
            return payload
        
        def track_get_user_call(*args, **kwargs):
            call_order.append("get_user")
            return mock_user
        
        def track_generate_call(*args, **kwargs):
            call_order.append("generate")
            return new_tokens
        
        self.mock_jwt_gateway.validate_refresh_token.side_effect = track_validate_call
        self.mock_user_repository.get_by_id.side_effect = track_get_user_call
        self.mock_jwt_gateway.generate_tokens.side_effect = track_generate_call
        
        # Re-execute to track order
        result = self.use_case.execute(refresh_token)
        
        self.assertEqual(call_order, ["validate", "get_user", "generate"])

    def test_execute_generates_new_tokens_with_user_data(self):
        """Test that execute generates new tokens with correct user data."""
        # Arrange
        refresh_token = "valid_refresh_token"
        user_id = 42
        email = "user@example.com"

        payload = {"user_id": user_id, "email": email, "type": "refresh"}
        self.mock_jwt_gateway.validate_refresh_token.return_value = payload
        
        mock_user = Mock(spec=UserDomain, id=user_id, email=email)
        self.mock_user_repository.get_by_id.return_value = mock_user
        
        new_tokens = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
        }
        self.mock_jwt_gateway.generate_tokens.return_value = new_tokens

        # Act
        result = self.use_case.execute(refresh_token)

        # Assert
        self.mock_jwt_gateway.generate_tokens.assert_called_once_with(user_id, email)

