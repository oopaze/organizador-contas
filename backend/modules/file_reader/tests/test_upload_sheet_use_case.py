"""
Unit tests for UploadSheetUseCase.

These tests verify that the use case correctly uploads spreadsheet files.
Celery tasks are mocked to avoid async processing.
"""
from unittest.mock import Mock, patch
from django.test import SimpleTestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from modules.file_reader.use_cases.upload_sheet import UploadSheetUseCase
from modules.file_reader.domains.file import FileDomain


class TestUploadSheetUseCase(SimpleTestCase):
    """Test UploadSheetUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_file_repository = Mock()
        self.mock_file_factory = Mock()
        self.mock_file_serializer = Mock()

        self.use_case = UploadSheetUseCase(
            file_repository=self.mock_file_repository,
            file_factory=self.mock_file_factory,
            file_serializer=self.mock_file_serializer,
        )

    @patch('modules.file_reader.tasks.process_sheet_upload')
    def test_execute_uploads_file_and_queues_task(self, mock_process_task):
        """Test that execute uploads file and queues processing task."""
        # Arrange
        user_id = 1
        uploaded_file = SimpleUploadedFile("test.xlsx", b"fake excel content")
        
        mock_file_domain = Mock(spec=FileDomain)
        mock_saved_file = Mock(spec=FileDomain)
        mock_saved_file.id = "123"
        
        self.mock_file_factory.build.return_value = mock_file_domain
        self.mock_file_repository.create.return_value = mock_saved_file
        self.mock_file_serializer.serialize.return_value = {"id": "123", "name": "test.xlsx"}

        # Act
        result = self.use_case.execute(uploaded_file, user_id)

        # Assert
        self.mock_file_factory.build.assert_called_once_with(uploaded_file)
        self.mock_file_repository.create.assert_called_once_with(mock_file_domain, user_id)
        mock_process_task.delay.assert_called_once_with(
            file_id="123",
            user_id=user_id,
            model="deepseek-chat",
            user_provided_description=None,
        )
        self.assertEqual(result["id"], "123")

    @patch('modules.file_reader.tasks.process_sheet_upload')
    def test_execute_with_custom_model(self, mock_process_task):
        """Test that execute passes custom model to processing task."""
        # Arrange
        user_id = 1
        model = "custom-model"
        uploaded_file = SimpleUploadedFile("test.xlsx", b"fake excel content")
        
        mock_file_domain = Mock(spec=FileDomain)
        mock_saved_file = Mock(spec=FileDomain)
        mock_saved_file.id = "123"
        
        self.mock_file_factory.build.return_value = mock_file_domain
        self.mock_file_repository.create.return_value = mock_saved_file
        self.mock_file_serializer.serialize.return_value = {"id": "123"}

        # Act
        self.use_case.execute(uploaded_file, user_id, model=model)

        # Assert
        mock_process_task.delay.assert_called_once_with(
            file_id="123",
            user_id=user_id,
            model=model,
            user_provided_description=None,
        )

    @patch('modules.file_reader.tasks.process_sheet_upload')
    def test_execute_with_user_description(self, mock_process_task):
        """Test that execute passes user description to processing task."""
        # Arrange
        user_id = 1
        description = "Monthly expenses from January"
        uploaded_file = SimpleUploadedFile("test.xlsx", b"fake excel content")
        
        mock_file_domain = Mock(spec=FileDomain)
        mock_saved_file = Mock(spec=FileDomain)
        mock_saved_file.id = "123"
        
        self.mock_file_factory.build.return_value = mock_file_domain
        self.mock_file_repository.create.return_value = mock_saved_file
        self.mock_file_serializer.serialize.return_value = {"id": "123"}

        # Act
        self.use_case.execute(uploaded_file, user_id, user_provided_description=description)

        # Assert
        mock_process_task.delay.assert_called_once_with(
            file_id="123",
            user_id=user_id,
            model="deepseek-chat",
            user_provided_description=description,
        )

    @patch('modules.file_reader.tasks.process_sheet_upload')
    def test_execute_saves_file_before_queuing_task(self, mock_process_task):
        """Test that file is saved before queuing the processing task."""
        # Arrange
        user_id = 1
        uploaded_file = SimpleUploadedFile("test.xlsx", b"fake excel content")
        
        mock_file_domain = Mock(spec=FileDomain)
        mock_saved_file = Mock(spec=FileDomain)
        mock_saved_file.id = "123"
        
        call_order = []
        self.mock_file_factory.build.return_value = mock_file_domain
        self.mock_file_repository.create.side_effect = lambda *args: (call_order.append("save"), mock_saved_file)[1]
        mock_process_task.delay.side_effect = lambda **kwargs: call_order.append("queue")
        self.mock_file_serializer.serialize.return_value = {"id": "123"}

        # Act
        self.use_case.execute(uploaded_file, user_id)

        # Assert
        self.assertEqual(call_order, ["save", "queue"])

    @patch('modules.file_reader.tasks.process_sheet_upload')
    def test_execute_returns_serialized_file(self, mock_process_task):
        """Test that execute returns the serialized file."""
        # Arrange
        user_id = 1
        uploaded_file = SimpleUploadedFile("test.xlsx", b"fake excel content")
        
        mock_file_domain = Mock(spec=FileDomain)
        mock_saved_file = Mock(spec=FileDomain)
        mock_saved_file.id = "123"
        
        self.mock_file_factory.build.return_value = mock_file_domain
        self.mock_file_repository.create.return_value = mock_saved_file
        self.mock_file_serializer.serialize.return_value = {
            "id": "123",
            "name": "test.xlsx",
            "status": "processing"
        }

        # Act
        result = self.use_case.execute(uploaded_file, user_id)

        # Assert
        self.mock_file_serializer.serialize.assert_called_once_with(mock_saved_file)
        self.assertEqual(result["id"], "123")
        self.assertEqual(result["name"], "test.xlsx")
        self.assertEqual(result["status"], "processing")

