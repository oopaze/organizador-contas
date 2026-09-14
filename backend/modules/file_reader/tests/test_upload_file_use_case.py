"""
Unit tests for UploadFileUseCase.

These tests verify that the use case correctly uploads files and processes them with AI.
All external dependencies (AI, file storage, repositories) are mocked.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from modules.file_reader.use_cases.upload_file import UploadFileUseCase
from modules.file_reader.domains.file import FileDomain
from modules.file_reader.domains.ai_call import AICallDomain


class TestUploadFileUseCase(TestCase):
    """Test UploadFileUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_file_repository = Mock()
        self.mock_file_factory = Mock()
        self.mock_file_serializer = Mock()
        self.mock_transpose_use_case = Mock()
        self.mock_ai_call_repository = Mock()
        self.mock_ai_call_factory = Mock()
        self.mock_ask_use_case = Mock()
        self.mock_remove_password_use_case = Mock()

        self.use_case = UploadFileUseCase(
            file_repository=self.mock_file_repository,
            file_factory=self.mock_file_factory,
            file_serializer=self.mock_file_serializer,
            transpose_file_bill_to_models_use_case=self.mock_transpose_use_case,
            ai_call_repository=self.mock_ai_call_repository,
            ai_call_factory=self.mock_ai_call_factory,
            ask_use_case=self.mock_ask_use_case,
            remove_pdf_password_use_case=self.mock_remove_password_use_case,
        )

    def test_execute_uploads_and_processes_file(self):
        """Test that execute uploads a file and processes it with AI."""
        # Arrange
        user_id = 1
        uploaded_file = SimpleUploadedFile("test.pdf", b"fake pdf content")
        
        mock_file_domain = Mock(spec=FileDomain)
        mock_file_domain.id = "123"
        mock_file_domain.extract_text_from_pdf.return_value = "Extracted PDF text"
        
        mock_saved_file = Mock(spec=FileDomain)
        mock_saved_file.id = "123"
        mock_saved_file.extract_text_from_pdf.return_value = "Extracted PDF text"
        
        mock_updated_file = Mock(spec=FileDomain)
        mock_updated_file.id = "123"
        
        mock_ai_call = Mock(spec=AICallDomain)
        mock_ai_call.id = "ai_123"
        
        self.mock_file_factory.build.return_value = mock_file_domain
        self.mock_file_repository.create.return_value = mock_saved_file
        self.mock_ask_use_case.execute.return_value = "ai_123"
        self.mock_ai_call_repository.get.return_value = mock_ai_call
        self.mock_file_repository.update.return_value = mock_updated_file
        self.mock_file_serializer.serialize.return_value = {"id": "123"}

        # Act
        result = self.use_case.execute(uploaded_file, user_id)

        # Assert
        self.mock_file_factory.build.assert_called_once_with(uploaded_file)
        self.mock_file_repository.create.assert_called_once_with(mock_file_domain, user_id)
        mock_saved_file.extract_text_from_pdf.assert_called_once_with(None)
        self.mock_ask_use_case.execute.assert_called_once()
        self.mock_ai_call_repository.get.assert_called_once_with("ai_123")
        mock_saved_file.update_ai_info.assert_called_once_with(mock_ai_call)
        self.mock_file_repository.update.assert_called_once_with(mock_saved_file)
        self.mock_transpose_use_case.execute.assert_called_once_with("123", user_id, False)
        self.assertEqual(result["id"], "123")

    def test_execute_with_password_removes_password_first(self):
        """Test that execute removes password before processing if provided."""
        # Arrange
        user_id = 1
        password = "test123"
        uploaded_file = SimpleUploadedFile("test.pdf", b"fake pdf content")
        
        mock_file_domain = Mock(spec=FileDomain)
        mock_saved_file = Mock(spec=FileDomain)
        mock_saved_file.id = "123"
        mock_saved_file.extract_text_from_pdf.return_value = "Extracted PDF text"
        mock_updated_file = Mock(spec=FileDomain)
        mock_updated_file.id = "123"
        mock_ai_call = Mock(spec=AICallDomain)
        
        self.mock_file_factory.build.return_value = mock_file_domain
        self.mock_file_repository.create.return_value = mock_saved_file
        self.mock_ask_use_case.execute.return_value = "ai_123"
        self.mock_ai_call_repository.get.return_value = mock_ai_call
        self.mock_file_repository.update.return_value = mock_updated_file
        self.mock_file_serializer.serialize.return_value = {"id": "123"}

        # Act
        self.use_case.execute(uploaded_file, user_id, password=password)

        # Assert
        self.mock_remove_password_use_case.execute.assert_called_once_with(mock_saved_file, password)
        mock_saved_file.extract_text_from_pdf.assert_called_once_with(password)

    def test_execute_without_password_skips_password_removal(self):
        """Test that execute skips password removal when no password is provided."""
        # Arrange
        user_id = 1
        uploaded_file = SimpleUploadedFile("test.pdf", b"fake pdf content")
        
        mock_file_domain = Mock(spec=FileDomain)
        mock_saved_file = Mock(spec=FileDomain)
        mock_saved_file.id = "123"
        mock_saved_file.extract_text_from_pdf.return_value = "Extracted PDF text"
        mock_updated_file = Mock(spec=FileDomain)
        mock_updated_file.id = "123"
        mock_ai_call = Mock(spec=AICallDomain)
        
        self.mock_file_factory.build.return_value = mock_file_domain
        self.mock_file_repository.create.return_value = mock_saved_file
        self.mock_ask_use_case.execute.return_value = "ai_123"
        self.mock_ai_call_repository.get.return_value = mock_ai_call
        self.mock_file_repository.update.return_value = mock_updated_file
        self.mock_file_serializer.serialize.return_value = {"id": "123"}

        # Act
        self.use_case.execute(uploaded_file, user_id)

        # Assert
        self.mock_remove_password_use_case.execute.assert_not_called()

    def test_execute_with_create_in_future_months(self):
        """Test that execute passes create_in_future_months flag to transpose use case."""
        # Arrange
        user_id = 1
        uploaded_file = SimpleUploadedFile("test.pdf", b"fake pdf content")

        mock_file_domain = Mock(spec=FileDomain)
        mock_saved_file = Mock(spec=FileDomain)
        mock_saved_file.id = "123"
        mock_saved_file.extract_text_from_pdf.return_value = "Extracted PDF text"
        mock_updated_file = Mock(spec=FileDomain)
        mock_updated_file.id = "123"
        mock_ai_call = Mock(spec=AICallDomain)

        self.mock_file_factory.build.return_value = mock_file_domain
        self.mock_file_repository.create.return_value = mock_saved_file
        self.mock_ask_use_case.execute.return_value = "ai_123"
        self.mock_ai_call_repository.get.return_value = mock_ai_call
        self.mock_file_repository.update.return_value = mock_updated_file
        self.mock_file_serializer.serialize.return_value = {"id": "123"}

        # Act
        self.use_case.execute(uploaded_file, user_id, create_in_future_months=True)

        # Assert
        self.mock_transpose_use_case.execute.assert_called_once_with("123", user_id, True)

    def test_execute_calls_ask_use_case_with_correct_prompt(self):
        """Test that execute calls AI with the correct prompt format."""
        # Arrange
        user_id = 1
        uploaded_file = SimpleUploadedFile("test.pdf", b"fake pdf content")
        model = "test-model"

        mock_file_domain = Mock(spec=FileDomain)
        mock_saved_file = Mock(spec=FileDomain)
        mock_saved_file.id = "123"
        mock_saved_file.extract_text_from_pdf.return_value = "Extracted PDF text"
        mock_updated_file = Mock(spec=FileDomain)
        mock_updated_file.id = "123"
        mock_ai_call = Mock(spec=AICallDomain)

        self.mock_file_factory.build.return_value = mock_file_domain
        self.mock_file_repository.create.return_value = mock_saved_file
        self.mock_ask_use_case.execute.return_value = "ai_123"
        self.mock_ai_call_repository.get.return_value = mock_ai_call
        self.mock_file_repository.update.return_value = mock_updated_file
        self.mock_file_serializer.serialize.return_value = {"id": "123"}

        # Act
        self.use_case.execute(uploaded_file, user_id, model=model)

        # Assert
        call_args = self.mock_ask_use_case.execute.call_args
        self.assertEqual(call_args[0][1], user_id)
        self.assertEqual(call_args[1]["response_format"], "json_object")
        self.assertEqual(call_args[1]["model"], model)
        # Verify prompt contains file name and extracted text
        prompt = call_args[0][0]
        self.assertIn("test.pdf", prompt[1])
        self.assertIn("Extracted PDF text", prompt[1])

