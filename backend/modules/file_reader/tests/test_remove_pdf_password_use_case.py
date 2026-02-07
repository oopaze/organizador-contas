"""
Unit tests for RemovePDFPasswordUseCase.

These tests verify that the use case correctly removes passwords from PDFs.
PyPDF2 library is mocked to avoid file system operations.
"""
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from django.test import SimpleTestCase

from modules.file_reader.use_cases.remover_pdf_password import RemovePDFPasswordUseCase
from modules.file_reader.domains.file import FileDomain


class TestRemovePDFPasswordUseCase(SimpleTestCase):
    """Test RemovePDFPasswordUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.use_case = RemovePDFPasswordUseCase()

    @patch('modules.file_reader.use_cases.remover_pdf_password.PyPDF2')
    def test_execute_removes_password_from_encrypted_pdf(self, mock_pypdf2):
        """Test that execute removes password from an encrypted PDF."""
        # Arrange
        password = "test123"
        mock_file = Mock(spec=FileDomain)
        mock_uploaded_file = Mock()
        mock_file.uploaded_file = mock_uploaded_file
        
        # Mock file operations
        mock_file_content = BytesIO(b"fake pdf content")
        mock_uploaded_file.open = MagicMock(return_value=MagicMock(__enter__=Mock(return_value=mock_file_content), __exit__=Mock()))
        mock_uploaded_file.save = Mock()
        
        # Mock PyPDF2
        mock_reader = Mock()
        mock_reader.is_encrypted = True
        mock_reader.decrypt.return_value = True
        mock_reader.pages = [Mock(), Mock()]
        
        mock_writer = Mock()
        mock_output = BytesIO()
        mock_writer.write.return_value = None
        
        mock_pypdf2.PdfReader.return_value = mock_reader
        mock_pypdf2.PdfWriter.return_value = mock_writer

        # Act
        with patch('modules.file_reader.use_cases.remover_pdf_password.io.BytesIO', return_value=mock_output):
            self.use_case.execute(mock_file, password)

        # Assert
        mock_reader.decrypt.assert_called_once_with(password)
        self.assertEqual(mock_writer.add_page.call_count, 2)
        mock_uploaded_file.save.assert_called_once()

    @patch('modules.file_reader.use_cases.remover_pdf_password.PyPDF2')
    def test_execute_skips_non_encrypted_pdf(self, mock_pypdf2):
        """Test that execute skips non-encrypted PDFs."""
        # Arrange
        password = "test123"
        mock_file = Mock(spec=FileDomain)
        mock_uploaded_file = Mock()
        mock_file.uploaded_file = mock_uploaded_file
        
        # Mock file operations
        mock_file_content = BytesIO(b"fake pdf content")
        mock_uploaded_file.open = MagicMock(return_value=MagicMock(__enter__=Mock(return_value=mock_file_content), __exit__=Mock()))
        
        # Mock PyPDF2
        mock_reader = Mock()
        mock_reader.is_encrypted = False
        
        mock_pypdf2.PdfReader.return_value = mock_reader

        # Act
        self.use_case.execute(mock_file, password)

        # Assert
        mock_reader.decrypt.assert_not_called()
        mock_uploaded_file.save.assert_not_called()

    @patch('modules.file_reader.use_cases.remover_pdf_password.PyPDF2')
    def test_execute_raises_exception_on_invalid_password(self, mock_pypdf2):
        """Test that execute raises exception when password is invalid."""
        # Arrange
        password = "wrong_password"
        mock_file = Mock(spec=FileDomain)
        mock_uploaded_file = Mock()
        mock_file.uploaded_file = mock_uploaded_file
        
        # Mock file operations
        mock_file_content = BytesIO(b"fake pdf content")
        mock_uploaded_file.open = MagicMock(return_value=MagicMock(__enter__=Mock(return_value=mock_file_content), __exit__=Mock()))
        
        # Mock PyPDF2
        mock_reader = Mock()
        mock_reader.is_encrypted = True
        mock_reader.decrypt.side_effect = Exception("Invalid password")
        
        mock_pypdf2.PdfReader.return_value = mock_reader

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.use_case.execute(mock_file, password)
        
        self.assertIn("Invalid password", str(context.exception))

    @patch('modules.file_reader.use_cases.remover_pdf_password.PyPDF2')
    def test_execute_copies_all_pages(self, mock_pypdf2):
        """Test that execute copies all pages from the original PDF."""
        # Arrange
        password = "test123"
        mock_file = Mock(spec=FileDomain)
        mock_uploaded_file = Mock()
        mock_file.uploaded_file = mock_uploaded_file
        
        # Mock file operations
        mock_file_content = BytesIO(b"fake pdf content")
        mock_uploaded_file.open = MagicMock(return_value=MagicMock(__enter__=Mock(return_value=mock_file_content), __exit__=Mock()))
        mock_uploaded_file.save = Mock()
        
        # Mock PyPDF2 with 5 pages
        mock_reader = Mock()
        mock_reader.is_encrypted = True
        mock_reader.decrypt.return_value = True
        mock_reader.pages = [Mock() for _ in range(5)]
        
        mock_writer = Mock()
        mock_output = BytesIO()
        
        mock_pypdf2.PdfReader.return_value = mock_reader
        mock_pypdf2.PdfWriter.return_value = mock_writer

        # Act
        with patch('modules.file_reader.use_cases.remover_pdf_password.io.BytesIO', return_value=mock_output):
            self.use_case.execute(mock_file, password)

        # Assert
        self.assertEqual(mock_writer.add_page.call_count, 5)

