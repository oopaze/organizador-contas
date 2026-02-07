from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.userdata.use_cases.update_profile import UpdateProfileUseCase
from modules.userdata.domains.profile import ProfileDomain


class TestUpdateProfileUseCase(SimpleTestCase):
    def setUp(self):
        """Set up test dependencies."""
        self.mock_profile_repository = Mock()
        self.mock_profile_serializer = Mock()

        self.use_case = UpdateProfileUseCase(
            profile_repository=self.mock_profile_repository,
            profile_serializer=self.mock_profile_serializer,
        )

    def test_execute_updates_profile(self):
        """Test that execute updates a profile successfully."""
        # Arrange
        profile_id = 1
        update_data = {
            "first_name": "John",
            "last_name": "Doe",
            "bio": "Software Developer",
            "salary": 5000.0,
        }

        mock_profile = Mock(spec=ProfileDomain, id=profile_id)
        self.mock_profile_repository.get.return_value = mock_profile
        
        mock_updated_profile = Mock(
            spec=ProfileDomain,
            id=profile_id,
            first_name="John",
            last_name="Doe",
            bio="Software Developer",
            salary=5000.0,
        )
        self.mock_profile_repository.update.return_value = mock_updated_profile
        
        serialized_profile = {
            "id": profile_id,
            "first_name": "John",
            "last_name": "Doe",
            "bio": "Software Developer",
            "salary": 5000.0,
        }
        self.mock_profile_serializer.serialize.return_value = serialized_profile

        # Act
        result = self.use_case.execute(profile_id, update_data)

        # Assert
        self.mock_profile_repository.get.assert_called_once_with(profile_id)
        mock_profile.update.assert_called_once_with(update_data)
        self.mock_profile_repository.update.assert_called_once_with(mock_profile)
        self.mock_profile_serializer.serialize.assert_called_once_with(mock_updated_profile)
        
        self.assertEqual(result, serialized_profile)
        self.assertEqual(result["first_name"], "John")
        self.assertEqual(result["last_name"], "Doe")

    def test_execute_updates_partial_fields(self):
        """Test that execute updates only provided fields."""
        # Arrange
        profile_id = 1
        update_data = {"first_name": "Jane"}

        mock_profile = Mock(spec=ProfileDomain, id=profile_id)
        self.mock_profile_repository.get.return_value = mock_profile
        
        mock_updated_profile = Mock(spec=ProfileDomain, id=profile_id, first_name="Jane")
        self.mock_profile_repository.update.return_value = mock_updated_profile
        
        serialized_profile = {"id": profile_id, "first_name": "Jane"}
        self.mock_profile_serializer.serialize.return_value = serialized_profile

        # Act
        result = self.use_case.execute(profile_id, update_data)

        # Assert
        mock_profile.update.assert_called_once_with(update_data)
        self.assertEqual(result["first_name"], "Jane")

    def test_execute_updates_bio(self):
        """Test that execute updates bio field."""
        # Arrange
        profile_id = 1
        update_data = {"bio": "New bio text"}

        mock_profile = Mock(spec=ProfileDomain, id=profile_id)
        self.mock_profile_repository.get.return_value = mock_profile
        
        mock_updated_profile = Mock(spec=ProfileDomain, id=profile_id, bio="New bio text")
        self.mock_profile_repository.update.return_value = mock_updated_profile
        
        serialized_profile = {"id": profile_id, "bio": "New bio text"}
        self.mock_profile_serializer.serialize.return_value = serialized_profile

        # Act
        result = self.use_case.execute(profile_id, update_data)

        # Assert
        self.assertEqual(result["bio"], "New bio text")

    def test_execute_updates_salary(self):
        """Test that execute updates salary field."""
        # Arrange
        profile_id = 1
        update_data = {"salary": 7500.0}

        mock_profile = Mock(spec=ProfileDomain, id=profile_id)
        self.mock_profile_repository.get.return_value = mock_profile
        
        mock_updated_profile = Mock(spec=ProfileDomain, id=profile_id, salary=7500.0)
        self.mock_profile_repository.update.return_value = mock_updated_profile
        
        serialized_profile = {"id": profile_id, "salary": 7500.0}
        self.mock_profile_serializer.serialize.return_value = serialized_profile

        # Act
        result = self.use_case.execute(profile_id, update_data)

        # Assert
        self.assertEqual(result["salary"], 7500.0)

    def test_execute_calls_profile_update_method(self):
        """Test that execute calls the profile's update method."""
        # Arrange
        profile_id = 1
        update_data = {"first_name": "John", "last_name": "Doe"}

        mock_profile = Mock(spec=ProfileDomain, id=profile_id)
        self.mock_profile_repository.get.return_value = mock_profile
        
        mock_updated_profile = Mock(spec=ProfileDomain, id=profile_id)
        self.mock_profile_repository.update.return_value = mock_updated_profile
        
        self.mock_profile_serializer.serialize.return_value = {"id": profile_id}

        # Act
        self.use_case.execute(profile_id, update_data)

        # Assert
        mock_profile.update.assert_called_once_with(update_data)

    def test_execute_returns_serialized_updated_profile(self):
        """Test that execute returns the serialized updated profile."""
        # Arrange
        profile_id = 1
        update_data = {"first_name": "John"}

        mock_profile = Mock(spec=ProfileDomain, id=profile_id)
        self.mock_profile_repository.get.return_value = mock_profile
        
        mock_updated_profile = Mock(spec=ProfileDomain, id=profile_id, first_name="John")
        self.mock_profile_repository.update.return_value = mock_updated_profile
        
        serialized_profile = {
            "id": profile_id,
            "first_name": "John",
            "last_name": "",
            "bio": "",
            "salary": 0.0,
        }
        self.mock_profile_serializer.serialize.return_value = serialized_profile

        # Act
        result = self.use_case.execute(profile_id, update_data)

        # Assert
        self.mock_profile_serializer.serialize.assert_called_once_with(mock_updated_profile)
        self.assertEqual(result, serialized_profile)

