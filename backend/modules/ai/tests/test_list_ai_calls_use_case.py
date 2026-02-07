"""
Unit tests for ListAICallsUseCase.

These tests verify that the use case correctly lists AI calls.
All external dependencies are mocked.
"""
from unittest.mock import Mock
from django.test import SimpleTestCase

from modules.ai.use_cases.ai_call.list_ai_calls import ListAICallsUseCase
from modules.ai.domains.ai_response import AIResponseDomain


class TestListAICallsUseCase(SimpleTestCase):
    """Test ListAICallsUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_ai_call_repository = Mock()
        self.mock_ai_call_serializer = Mock()

        self.use_case = ListAICallsUseCase(
            ai_call_repository=self.mock_ai_call_repository,
            ai_call_serializer=self.mock_ai_call_serializer,
        )

    def test_execute_returns_serialized_ai_calls(self):
        """Test that execute returns a list of serialized AI calls."""
        # Arrange
        user_id = 1
        mock_ai_call1 = Mock(spec=AIResponseDomain)
        mock_ai_call2 = Mock(spec=AIResponseDomain)
        
        self.mock_ai_call_repository.get_all_by_user_id.return_value = [mock_ai_call1, mock_ai_call2]
        self.mock_ai_call_serializer.serialize.side_effect = [
            {"id": "1", "model": "gpt-4"},
            {"id": "2", "model": "gpt-3.5"},
        ]

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.mock_ai_call_repository.get_all_by_user_id.assert_called_once_with(
            user_id, None, None, None
        )
        self.assertEqual(self.mock_ai_call_serializer.serialize.call_count, 2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "1")
        self.assertEqual(result[1]["id"], "2")

    def test_execute_with_filter_by_model(self):
        """Test that execute filters AI calls by model."""
        # Arrange
        user_id = 1
        filter_by_model = "gpt-4"
        mock_ai_call = Mock(spec=AIResponseDomain)
        
        self.mock_ai_call_repository.get_all_by_user_id.return_value = [mock_ai_call]
        self.mock_ai_call_serializer.serialize.return_value = {"id": "1", "model": "gpt-4"}

        # Act
        result = self.use_case.execute(user_id, filter_by_model=filter_by_model)

        # Assert
        self.mock_ai_call_repository.get_all_by_user_id.assert_called_once_with(
            user_id, filter_by_model, None, None
        )
        self.assertEqual(len(result), 1)

    def test_execute_with_date_range(self):
        """Test that execute filters AI calls by date range."""
        # Arrange
        user_id = 1
        due_date_start = "2026-01-01"
        due_date_end = "2026-01-31"
        mock_ai_call = Mock(spec=AIResponseDomain)
        
        self.mock_ai_call_repository.get_all_by_user_id.return_value = [mock_ai_call]
        self.mock_ai_call_serializer.serialize.return_value = {"id": "1"}

        # Act
        result = self.use_case.execute(user_id, due_date_start=due_date_start, due_date_end=due_date_end)

        # Assert
        self.mock_ai_call_repository.get_all_by_user_id.assert_called_once_with(
            user_id, None, due_date_start, due_date_end
        )
        self.assertEqual(len(result), 1)

    def test_execute_with_all_filters(self):
        """Test that execute handles all filters together."""
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
        self.assertEqual(result, [])

    def test_execute_with_empty_results(self):
        """Test that execute handles empty AI call list."""
        # Arrange
        user_id = 1
        self.mock_ai_call_repository.get_all_by_user_id.return_value = []

        # Act
        result = self.use_case.execute(user_id)

        # Assert
        self.mock_ai_call_repository.get_all_by_user_id.assert_called_once()
        self.mock_ai_call_serializer.serialize.assert_not_called()
        self.assertEqual(result, [])

