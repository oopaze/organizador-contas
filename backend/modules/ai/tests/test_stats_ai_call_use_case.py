"""
Unit tests for StatsAICallUseCase.

These tests verify that the use case correctly calculates AI call statistics.
All external dependencies are mocked.
"""
from unittest.mock import Mock
from decimal import Decimal
from django.test import SimpleTestCase

from modules.ai.use_cases.ai_call.stats_ai_call import StatsAICallUseCase
from modules.ai.domains.ai_call import AICallDomain


class TestStatsAICallUseCase(SimpleTestCase):
    """Test StatsAICallUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_ai_call_repository = Mock()
        self.use_case = StatsAICallUseCase(ai_call_repository=self.mock_ai_call_repository)

    def test_execute_calculates_stats_for_ai_calls(self):
        """Test that execute calculates statistics for AI calls."""
        # Arrange
        user_id = 1
        mock_ai_call1 = Mock(spec=AICallDomain)
        mock_ai_call1.total_tokens = 100
        mock_ai_call1.input_used_tokens = 60
        mock_ai_call1.output_used_tokens = 40
        mock_ai_call1.is_error = False
        mock_ai_call1.model = "gpt-4"
        mock_ai_call1.model_prices = Mock(return_value={
            "input": Decimal("0.01"),
            "output": Decimal("0.02"),
            "total": Decimal("0.03"),
        })

        mock_ai_call2 = Mock(spec=AICallDomain)
        mock_ai_call2.total_tokens = 200
        mock_ai_call2.input_used_tokens = 120
        mock_ai_call2.output_used_tokens = 80
        mock_ai_call2.is_error = False
        mock_ai_call2.model = "gpt-3.5"
        mock_ai_call2.model_prices = Mock(return_value={
            "input": Decimal("0.005"),
            "output": Decimal("0.01"),
            "total": Decimal("0.015"),
        })
        
        self.mock_ai_call_repository.get_all_by_user_id.return_value = [mock_ai_call1, mock_ai_call2]

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.assertEqual(result["total_calls"], 2)
        self.assertEqual(result["total_tokens"], 300)
        self.assertEqual(result["total_input_tokens"], 180)
        self.assertEqual(result["total_output_tokens"], 120)
        self.assertEqual(result["total_errors"], 0)
        self.assertEqual(result["amount_spent"]["total"], Decimal("0.045"))

    def test_execute_counts_errors(self):
        """Test that execute correctly counts errors."""
        # Arrange
        user_id = 1
        mock_ai_call1 = Mock(spec=AICallDomain)
        mock_ai_call1.total_tokens = 100
        mock_ai_call1.input_used_tokens = 60
        mock_ai_call1.output_used_tokens = 40
        mock_ai_call1.is_error = True
        mock_ai_call1.model = "gpt-4"
        mock_ai_call1.model_prices = Mock(return_value={
            "input": Decimal("0.01"),
            "output": Decimal("0.02"),
            "total": Decimal("0.03"),
        })

        mock_ai_call2 = Mock(spec=AICallDomain)
        mock_ai_call2.total_tokens = 200
        mock_ai_call2.input_used_tokens = 120
        mock_ai_call2.output_used_tokens = 80
        mock_ai_call2.is_error = True
        mock_ai_call2.model = "gpt-3.5"
        mock_ai_call2.model_prices = Mock(return_value={
            "input": Decimal("0.005"),
            "output": Decimal("0.01"),
            "total": Decimal("0.015"),
        })
        
        self.mock_ai_call_repository.get_all_by_user_id.return_value = [mock_ai_call1, mock_ai_call2]

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.assertEqual(result["total_errors"], 2)

    def test_execute_groups_stats_by_model(self):
        """Test that execute groups statistics by model."""
        # Arrange
        user_id = 1
        mock_ai_call1 = Mock(spec=AICallDomain)
        mock_ai_call1.total_tokens = 100
        mock_ai_call1.input_used_tokens = 60
        mock_ai_call1.output_used_tokens = 40
        mock_ai_call1.is_error = False
        mock_ai_call1.model = "gpt-4"
        mock_ai_call1.model_prices = Mock(return_value={
            "input": Decimal("0.01"),
            "output": Decimal("0.02"),
            "total": Decimal("0.03"),
        })

        mock_ai_call2 = Mock(spec=AICallDomain)
        mock_ai_call2.total_tokens = 150
        mock_ai_call2.input_used_tokens = 90
        mock_ai_call2.output_used_tokens = 60
        mock_ai_call2.is_error = False
        mock_ai_call2.model = "gpt-4"
        mock_ai_call2.model_prices = Mock(return_value={
            "input": Decimal("0.015"),
            "output": Decimal("0.03"),
            "total": Decimal("0.045"),
        })
        
        self.mock_ai_call_repository.get_all_by_user_id.return_value = [mock_ai_call1, mock_ai_call2]

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.assertIn("gpt-4", result["models_stats"])
        self.assertEqual(result["models_stats"]["gpt-4"]["count"], 2)
        self.assertEqual(result["models_stats"]["gpt-4"]["total_tokens"], 250)
        self.assertEqual(result["models_stats"]["gpt-4"]["total_input_tokens"], 150)
        self.assertEqual(result["models_stats"]["gpt-4"]["total_output_tokens"], 100)
        self.assertEqual(result["models_stats"]["gpt-4"]["total_spent"], Decimal("0.075"))

    def test_execute_with_filters(self):
        """Test that execute passes filters to repository."""
        # Arrange
        user_id = 1
        filter_by_model = "gpt-4"
        due_date_start = "2026-01-01"
        due_date_end = "2026-01-31"
        
        self.mock_ai_call_repository.get_all_by_user_id.return_value = []

        # Act
        result = self.use_case.execute(
            user_id,
            filter_by_model=filter_by_model,
            due_date_start=due_date_start,
            due_date_end=due_date_end
        )

        # Assert
        self.mock_ai_call_repository.get_all_by_user_id.assert_called_once_with(
            user_id, filter_by_model, due_date_start, due_date_end
        )

    def test_calculate_stats_with_empty_list(self):
        """Test that calculate_stats handles empty AI call list."""
        # Arrange
        ai_calls = []

        # Act
        result = self.use_case.calculate_stats(ai_calls)

        # Assert
        self.assertEqual(result["total_calls"], 0)
        self.assertEqual(result["total_tokens"], 0)
        self.assertEqual(result["total_input_tokens"], 0)
        self.assertEqual(result["total_output_tokens"], 0)
        self.assertEqual(result["total_errors"], 0)
        self.assertEqual(result["models_stats"], {})
        self.assertEqual(result["amount_spent"]["total"], Decimal("0"))

