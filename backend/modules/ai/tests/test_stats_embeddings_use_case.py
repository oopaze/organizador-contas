"""
Unit tests for StatsEmbeddingsUseCase.

These tests verify that the use case correctly calculates embedding statistics.
All external dependencies are mocked.
"""
from unittest.mock import Mock
from decimal import Decimal
from django.test import SimpleTestCase

from modules.ai.use_cases.embedding.stats_embeddings import StatsEmbeddingsUseCase
from modules.ai.domains.embedding import EmbeddingDomain


class TestStatsEmbeddingsUseCase(SimpleTestCase):
    """Test StatsEmbeddingsUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_embedding_repository = Mock()
        self.use_case = StatsEmbeddingsUseCase(embedding_repository=self.mock_embedding_repository)

    def test_execute_calculates_stats_for_embeddings(self):
        """Test that execute calculates statistics for embeddings."""
        # Arrange
        user_id = 1
        mock_embedding1 = Mock(spec=EmbeddingDomain)
        mock_embedding1.total_tokens = 100
        mock_embedding1.prompt_used_tokens = 100
        mock_embedding1.price = Decimal("0.01")
        mock_embedding1.model = "text-embedding-3-small"
        
        mock_embedding2 = Mock(spec=EmbeddingDomain)
        mock_embedding2.total_tokens = 200
        mock_embedding2.prompt_used_tokens = 200
        mock_embedding2.price = Decimal("0.02")
        mock_embedding2.model = "text-embedding-ada-002"
        
        self.mock_embedding_repository.get_all_by_user_id.return_value = [mock_embedding1, mock_embedding2]

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.assertEqual(result["total_embeddings"], 2)
        self.assertEqual(result["total_tokens"], 300)
        self.assertEqual(result["total_prompt_tokens"], 300)
        self.assertEqual(result["total_errors"], 0)
        self.assertEqual(result["amount_spent"], Decimal("0.03"))

    def test_execute_groups_stats_by_model(self):
        """Test that execute groups statistics by model."""
        # Arrange
        user_id = 1
        mock_embedding1 = Mock(spec=EmbeddingDomain)
        mock_embedding1.total_tokens = 100
        mock_embedding1.prompt_used_tokens = 100
        mock_embedding1.price = Decimal("0.01")
        mock_embedding1.model = "text-embedding-3-small"
        
        mock_embedding2 = Mock(spec=EmbeddingDomain)
        mock_embedding2.total_tokens = 150
        mock_embedding2.prompt_used_tokens = 150
        mock_embedding2.price = Decimal("0.015")
        mock_embedding2.model = "text-embedding-3-small"
        
        self.mock_embedding_repository.get_all_by_user_id.return_value = [mock_embedding1, mock_embedding2]

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.assertIn("text-embedding-3-small", result["models_stats"])
        self.assertEqual(result["models_stats"]["text-embedding-3-small"]["count"], 2)
        self.assertEqual(result["models_stats"]["text-embedding-3-small"]["total_tokens"], 250)
        self.assertEqual(result["models_stats"]["text-embedding-3-small"]["total_prompt_tokens"], 250)

    def test_execute_with_multiple_models(self):
        """Test that execute handles multiple different models."""
        # Arrange
        user_id = 1
        mock_embedding1 = Mock(spec=EmbeddingDomain)
        mock_embedding1.total_tokens = 100
        mock_embedding1.prompt_used_tokens = 100
        mock_embedding1.price = Decimal("0.01")
        mock_embedding1.model = "text-embedding-3-small"
        
        mock_embedding2 = Mock(spec=EmbeddingDomain)
        mock_embedding2.total_tokens = 200
        mock_embedding2.prompt_used_tokens = 200
        mock_embedding2.price = Decimal("0.02")
        mock_embedding2.model = "text-embedding-ada-002"
        
        mock_embedding3 = Mock(spec=EmbeddingDomain)
        mock_embedding3.total_tokens = 150
        mock_embedding3.prompt_used_tokens = 150
        mock_embedding3.price = Decimal("0.015")
        mock_embedding3.model = "text-embedding-3-large"
        
        self.mock_embedding_repository.get_all_by_user_id.return_value = [
            mock_embedding1, mock_embedding2, mock_embedding3
        ]

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.assertEqual(len(result["models_stats"]), 3)
        self.assertIn("text-embedding-3-small", result["models_stats"])
        self.assertIn("text-embedding-ada-002", result["models_stats"])
        self.assertIn("text-embedding-3-large", result["models_stats"])

    def test_execute_with_filters(self):
        """Test that execute passes filters to repository."""
        # Arrange
        user_id = 1
        due_date_start = "2026-01-01"
        due_date_end = "2026-01-31"
        
        self.mock_embedding_repository.get_all_by_user_id.return_value = []

        # Act
        result = self.use_case.execute(user_id, due_date_start=due_date_start, due_date_end=due_date_end)

        # Assert
        self.mock_embedding_repository.get_all_by_user_id.assert_called_once_with(
            user_id, due_date_start, due_date_end
        )

    def test_calculate_stats_with_empty_list(self):
        """Test that calculate_stats handles empty embedding list."""
        # Arrange
        embeddings = []

        # Act
        result = self.use_case.calculate_stats(embeddings)

        # Assert
        self.assertEqual(result["total_embeddings"], 0)
        self.assertEqual(result["total_tokens"], 0)
        self.assertEqual(result["total_prompt_tokens"], 0)
        self.assertEqual(result["total_errors"], 0)
        self.assertEqual(result["models_stats"], {})
        self.assertEqual(result["amount_spent"], Decimal("0"))

    def test_calculate_stats_accumulates_prices(self):
        """Test that calculate_stats correctly accumulates prices."""
        # Arrange
        mock_embedding1 = Mock(spec=EmbeddingDomain)
        mock_embedding1.total_tokens = 100
        mock_embedding1.prompt_used_tokens = 100
        mock_embedding1.price = Decimal("0.123")
        mock_embedding1.model = "test-model"
        
        mock_embedding2 = Mock(spec=EmbeddingDomain)
        mock_embedding2.total_tokens = 200
        mock_embedding2.prompt_used_tokens = 200
        mock_embedding2.price = Decimal("0.456")
        mock_embedding2.model = "test-model"
        
        embeddings = [mock_embedding1, mock_embedding2]

        # Act
        result = self.use_case.calculate_stats(embeddings)

        # Assert
        self.assertEqual(result["amount_spent"], Decimal("0.579"))

