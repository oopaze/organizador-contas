from unittest.mock import Mock
from django.test import TestCase

from modules.transactions.use_cases.tools.get_user_general_stats import GetUserGeneralStatsToolUseCase


class TestGetUserGeneralStatsToolUseCase(TestCase):
    """Test GetUserGeneralStatsToolUseCase with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_transaction_stats_use_case = Mock()
        self.user_id = 1

        self.use_case = GetUserGeneralStatsToolUseCase(
            transaction_stats_use_case=self.mock_transaction_stats_use_case,
            user_id=self.user_id,
        )

    def test_get_user_general_stats(self):
        """Test getting user general stats."""
        # Arrange
        due_date_start = "2026-03-01"
        due_date_end = "2026-03-31"

        mock_stats = {
            "incoming_total": 5000.00,
            "outgoing_total": 3000.00,
            "balance": 2000.00,
            "outgoing_from_actors": 1500.00,
        }

        self.mock_transaction_stats_use_case.execute.return_value = mock_stats

        # Act
        result = self.use_case.execute(due_date_start, due_date_end)

        # Assert
        self.mock_transaction_stats_use_case.execute.assert_called_once_with(
            self.user_id,
            due_date_start=due_date_start,
            due_date_end=due_date_end
        )
        
        # Verify the result contains the formatted stats
        self.assertIn("5000.0", result)  # incoming_total
        self.assertIn("3000.0", result)  # outgoing_total
        self.assertIn("2000.0", result)  # balance
        self.assertIn("1500.0", result)  # outgoing_from_actors

    def test_get_user_general_stats_with_zero_values(self):
        """Test getting user general stats with zero values."""
        # Arrange
        due_date_start = "2026-03-01"
        due_date_end = "2026-03-31"

        mock_stats = {
            "incoming_total": 0.00,
            "outgoing_total": 0.00,
            "balance": 0.00,
            "outgoing_from_actors": 0.00,
        }

        self.mock_transaction_stats_use_case.execute.return_value = mock_stats

        # Act
        result = self.use_case.execute(due_date_start, due_date_end)

        # Assert
        self.mock_transaction_stats_use_case.execute.assert_called_once_with(
            self.user_id,
            due_date_start=due_date_start,
            due_date_end=due_date_end
        )
        
        # Verify the result contains zero values
        self.assertIn("0.0", result)

    def test_get_user_general_stats_with_negative_balance(self):
        """Test getting user general stats with negative balance."""
        # Arrange
        due_date_start = "2026-03-01"
        due_date_end = "2026-03-31"

        mock_stats = {
            "incoming_total": 2000.00,
            "outgoing_total": 3000.00,
            "balance": -1000.00,
            "outgoing_from_actors": 500.00,
        }

        self.mock_transaction_stats_use_case.execute.return_value = mock_stats

        # Act
        result = self.use_case.execute(due_date_start, due_date_end)

        # Assert
        self.mock_transaction_stats_use_case.execute.assert_called_once_with(
            self.user_id,
            due_date_start=due_date_start,
            due_date_end=due_date_end
        )
        
        # Verify the result contains negative balance
        self.assertIn("-1000.0", result)

    def test_get_user_general_stats_method_alias(self):
        """Test that get_user_general_stats method works as an alias to execute."""
        # Arrange
        due_date_start = "2026-03-01"
        due_date_end = "2026-03-31"

        mock_stats = {
            "incoming_total": 1000.00,
            "outgoing_total": 500.00,
            "balance": 500.00,
            "outgoing_from_actors": 200.00,
        }

        self.mock_transaction_stats_use_case.execute.return_value = mock_stats

        # Act
        result = self.use_case.get_user_general_stats(due_date_start, due_date_end)

        # Assert
        self.mock_transaction_stats_use_case.execute.assert_called_once_with(
            self.user_id,
            due_date_start=due_date_start,
            due_date_end=due_date_end
        )
        self.assertIn("1000.0", result)

    def test_get_user_general_stats_different_period(self):
        """Test getting user general stats for a different period."""
        # Arrange
        due_date_start = "2026-01-01"
        due_date_end = "2026-12-31"

        mock_stats = {
            "incoming_total": 60000.00,
            "outgoing_total": 45000.00,
            "balance": 15000.00,
            "outgoing_from_actors": 20000.00,
        }

        self.mock_transaction_stats_use_case.execute.return_value = mock_stats

        # Act
        result = self.use_case.execute(due_date_start, due_date_end)

        # Assert
        self.mock_transaction_stats_use_case.execute.assert_called_once_with(
            self.user_id,
            due_date_start=due_date_start,
            due_date_end=due_date_end
        )
        self.assertIn("60000.0", result)
        self.assertIn("45000.0", result)

