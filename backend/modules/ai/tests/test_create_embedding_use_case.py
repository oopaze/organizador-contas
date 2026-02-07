"""
Unit tests for CreateEmbeddingUseCase.

These tests verify that the use case correctly creates embeddings.
All external dependencies (OpenAI gateway, repositories) are mocked.
"""
from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.ai.use_cases.create_embedding import CreateEmbeddingUseCase
from modules.ai.domains.embedding import EmbeddingDomain


class TestCreateEmbeddingUseCase(SimpleTestCase):
    """Test CreateEmbeddingUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_openai_gateway = Mock()
        self.mock_embedding_repository = Mock()
        self.mock_embedding_factory = Mock()

        self.use_case = CreateEmbeddingUseCase(
            openai_embedding_gateway=self.mock_openai_gateway,
            embedding_repository=self.mock_embedding_repository,
            embedding_factory=self.mock_embedding_factory,
        )

    def test_execute_creates_embedding(self):
        """Test that execute creates an embedding from text."""
        # Arrange
        text = "This is a test text for embedding"
        model = "text-embedding-3-small"
        
        mock_embedding_response = Mock()
        mock_embedding_domain = Mock(spec=EmbeddingDomain)
        mock_saved_embedding = Mock(spec=EmbeddingDomain)
        mock_saved_embedding.id = "embedding_123"
        
        self.mock_openai_gateway.generate_embedding.return_value = mock_embedding_response
        self.mock_embedding_factory.build_from_embedding_model_response.return_value = mock_embedding_domain
        self.mock_embedding_repository.create.return_value = mock_saved_embedding

        # Act
        result = self.use_case.execute(text, model)

        # Assert
        self.mock_openai_gateway.generate_embedding.assert_called_once_with(text, model)
        self.mock_embedding_factory.build_from_embedding_model_response.assert_called_once_with(
            mock_embedding_response, model
        )
        self.mock_embedding_repository.create.assert_called_once_with(mock_embedding_domain)
        self.assertEqual(result, "embedding_123")

    def test_execute_with_default_model(self):
        """Test that execute uses default model when not specified."""
        # Arrange
        text = "Test text"
        
        mock_embedding_response = Mock()
        mock_embedding_domain = Mock(spec=EmbeddingDomain)
        mock_saved_embedding = Mock(spec=EmbeddingDomain)
        mock_saved_embedding.id = "embedding_456"
        
        self.mock_openai_gateway.generate_embedding.return_value = mock_embedding_response
        self.mock_embedding_factory.build_from_embedding_model_response.return_value = mock_embedding_domain
        self.mock_embedding_repository.create.return_value = mock_saved_embedding

        # Act
        result = self.use_case.execute(text)

        # Assert
        # Should use default model (text-embedding-3-small)
        call_args = self.mock_openai_gateway.generate_embedding.call_args
        self.assertEqual(call_args[0][0], text)
        self.assertIn("text-embedding-3-small", str(call_args[0][1]))
        self.assertEqual(result, "embedding_456")

    def test_execute_returns_embedding_id(self):
        """Test that execute returns the embedding ID."""
        # Arrange
        text = "Another test text"
        model = "text-embedding-ada-002"
        
        mock_embedding_response = Mock()
        mock_embedding_domain = Mock(spec=EmbeddingDomain)
        mock_saved_embedding = Mock(spec=EmbeddingDomain)
        mock_saved_embedding.id = "embedding_789"
        
        self.mock_openai_gateway.generate_embedding.return_value = mock_embedding_response
        self.mock_embedding_factory.build_from_embedding_model_response.return_value = mock_embedding_domain
        self.mock_embedding_repository.create.return_value = mock_saved_embedding

        # Act
        result = self.use_case.execute(text, model)

        # Assert
        self.assertEqual(result, "embedding_789")

    def test_execute_calls_dependencies_in_correct_order(self):
        """Test that execute calls dependencies in the correct order."""
        # Arrange
        text = "Test text"
        model = "test-model"
        
        call_order = []
        
        mock_embedding_response = Mock()
        mock_embedding_domain = Mock(spec=EmbeddingDomain)
        mock_saved_embedding = Mock(spec=EmbeddingDomain)
        mock_saved_embedding.id = "embedding_123"
        
        self.mock_openai_gateway.generate_embedding.side_effect = lambda *args: (call_order.append("gateway"), mock_embedding_response)[1]
        self.mock_embedding_factory.build_from_embedding_model_response.side_effect = lambda *args: (call_order.append("factory"), mock_embedding_domain)[1]
        self.mock_embedding_repository.create.side_effect = lambda *args: (call_order.append("repository"), mock_saved_embedding)[1]

        # Act
        self.use_case.execute(text, model)

        # Assert
        self.assertEqual(call_order, ["gateway", "factory", "repository"])

