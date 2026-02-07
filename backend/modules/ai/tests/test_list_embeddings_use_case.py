"""
Unit tests for ListEmbeddingsUseCase.

These tests verify that the use case correctly lists embeddings.
All external dependencies are mocked.
"""
from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.ai.use_cases.embedding.list_embeddings import ListEmbeddingsUseCase
from modules.ai.domains.embedding import EmbeddingDomain


class TestListEmbeddingsUseCase(SimpleTestCase):
    """Test ListEmbeddingsUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_embedding_repository = Mock()
        self.mock_embedding_serializer = Mock()

        self.use_case = ListEmbeddingsUseCase(
            embedding_repository=self.mock_embedding_repository,
            embedding_serializer=self.mock_embedding_serializer,
        )

    def test_execute_returns_serialized_embeddings(self):
        """Test that execute returns a list of serialized embeddings."""
        # Arrange
        user_id = 1
        mock_embedding1 = Mock(spec=EmbeddingDomain)
        mock_embedding2 = Mock(spec=EmbeddingDomain)
        
        self.mock_embedding_repository.get_all_by_user_id.return_value = [mock_embedding1, mock_embedding2]
        self.mock_embedding_serializer.serialize.side_effect = [
            {"id": "1", "model": "text-embedding-3-small"},
            {"id": "2", "model": "text-embedding-ada-002"},
        ]

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.mock_embedding_repository.get_all_by_user_id.assert_called_once_with(user_id, None, None)
        self.assertEqual(self.mock_embedding_serializer.serialize.call_count, 2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "1")
        self.assertEqual(result[1]["id"], "2")

    def test_execute_with_date_range(self):
        """Test that execute filters embeddings by date range."""
        # Arrange
        user_id = 1
        due_date_start = "2026-01-01"
        due_date_end = "2026-01-31"
        mock_embedding = Mock(spec=EmbeddingDomain)
        
        self.mock_embedding_repository.get_all_by_user_id.return_value = [mock_embedding]
        self.mock_embedding_serializer.serialize.return_value = {"id": "1"}

        # Act
        result = self.use_case.execute(user_id, due_date_start=due_date_start, due_date_end=due_date_end)

        # Assert
        self.mock_embedding_repository.get_all_by_user_id.assert_called_once_with(
            user_id, due_date_start, due_date_end
        )
        self.assertEqual(len(result), 1)

    def test_execute_with_empty_results(self):
        """Test that execute handles empty embedding list."""
        # Arrange
        user_id = 1
        self.mock_embedding_repository.get_all_by_user_id.return_value = []

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.mock_embedding_repository.get_all_by_user_id.assert_called_once()
        self.mock_embedding_serializer.serialize.assert_not_called()
        self.assertEqual(result, [])

    def test_execute_serializes_all_embeddings(self):
        """Test that execute serializes all embeddings from repository."""
        # Arrange
        user_id = 1
        mock_embeddings = [Mock(spec=EmbeddingDomain) for _ in range(5)]
        
        self.mock_embedding_repository.get_all_by_user_id.return_value = mock_embeddings
        self.mock_embedding_serializer.serialize.side_effect = [
            {"id": str(i)} for i in range(5)
        ]

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.assertEqual(self.mock_embedding_serializer.serialize.call_count, 5)
        self.assertEqual(len(result), 5)
        for i, embedding_data in enumerate(result):
            self.assertEqual(embedding_data["id"], str(i))

    def test_execute_without_date_filters(self):
        """Test that execute works without date filters."""
        # Arrange
        user_id = 1
        mock_embedding = Mock(spec=EmbeddingDomain)
        
        self.mock_embedding_repository.get_all_by_user_id.return_value = [mock_embedding]
        self.mock_embedding_serializer.serialize.return_value = {"id": "1"}

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.mock_embedding_repository.get_all_by_user_id.assert_called_once_with(user_id, None, None)
        self.assertEqual(len(result), 1)

