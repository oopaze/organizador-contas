"""
Tests to ensure all AI tools return strings, not JSON/dict objects.

These tests verify that the tools are compatible with function calling
which requires string responses, not structured data.
"""
import json
from unittest.mock import Mock, MagicMock
from django.test import SimpleTestCase

from modules.transactions.use_cases.tools.get_transactions import GetTransactionsToolUseCase
from modules.transactions.use_cases.tools.get_actors import GetActorsToolUseCase
from modules.transactions.use_cases.tools.get_actor_detail import GetActorDetailToolUseCase
from modules.transactions.use_cases.tools.get_actor_stats import GetActorStatsToolUseCase
from modules.transactions.use_cases.tools.get_sub_transactions_from_transaction import (
    GetSubTransactionsFromTransactionToolUseCase,
)
from modules.transactions.use_cases.tools.get_user_general_stats import GetUserGeneralStatsToolUseCase


class TestGetTransactionsToolReturnsString(SimpleTestCase):
    """Test that GetTransactionsToolUseCase returns a string."""

    def setUp(self):
        self.mock_repository = Mock()
        self.mock_serializer = Mock()
        self.mock_factory = Mock()
        self.user_id = 1

        self.mock_repository.filter.return_value = []
        self.mock_serializer.serialize_many_for_tool.return_value = "No transactions found"

        self.use_case = GetTransactionsToolUseCase(
            transaction_repository=self.mock_repository,
            transaction_serializer=self.mock_serializer,
            transaction_factory=self.mock_factory,
            user_id=self.user_id,
        )

    def test_execute_returns_string(self):
        """Verify execute() returns a string type."""
        result = self.use_case.execute(
            due_date_start="2026-01-01",
            due_date_end="2026-01-31",
        )
        self.assertIsInstance(result, str)

    def test_execute_does_not_return_dict(self):
        """Verify execute() does not return a dict."""
        result = self.use_case.execute(
            due_date_start="2026-01-01",
            due_date_end="2026-01-31",
        )
        self.assertNotIsInstance(result, dict)

    def test_execute_does_not_return_list(self):
        """Verify execute() does not return a list."""
        result = self.use_case.execute(
            due_date_start="2026-01-01",
            due_date_end="2026-01-31",
        )
        self.assertNotIsInstance(result, list)


class TestGetActorsToolReturnsString(SimpleTestCase):
    """Test that GetActorsToolUseCase returns a string."""

    def setUp(self):
        self.mock_actor_repository = Mock()
        self.mock_actor_serializer = Mock()
        self.mock_sub_transaction_repository = Mock()
        self.user_id = 1

        self.mock_actor_repository.get_all.return_value = []
        self.mock_sub_transaction_repository.filter_by_actor_ids.return_value = []
        self.mock_actor_serializer.serialize_many_for_tool.return_value = "No actors found"

        self.use_case = GetActorsToolUseCase(
            actor_repository=self.mock_actor_repository,
            actor_serializer=self.mock_actor_serializer,
            sub_transaction_repository=self.mock_sub_transaction_repository,
            user_id=self.user_id,
        )

    def test_execute_returns_string(self):
        """Verify execute() returns a string type."""
        result = self.use_case.execute(
            due_date_start="2026-01-01",
            due_date_end="2026-01-31",
        )
        self.assertIsInstance(result, str)

    def test_execute_does_not_return_dict(self):
        """Verify execute() does not return a dict."""
        result = self.use_case.execute(
            due_date_start="2026-01-01",
            due_date_end="2026-01-31",
        )
        self.assertNotIsInstance(result, dict)


class TestGetActorDetailToolReturnsString(SimpleTestCase):
    """Test that GetActorDetailToolUseCase returns a string."""

    def setUp(self):
        self.mock_actor_repository = Mock()
        self.mock_actor_serializer = Mock()
        self.mock_sub_transaction_repository = Mock()
        self.mock_sub_transaction_serializer = Mock()
        self.user_id = 1

        mock_actor = Mock()
        mock_actor.sub_transactions = []
        self.mock_actor_repository.get.return_value = mock_actor
        self.mock_sub_transaction_repository.filter_by_actor_id.return_value = []
        self.mock_actor_serializer.serialize_for_tool.return_value = "Actor: Test"
        self.mock_sub_transaction_serializer.serialize_many_for_tool.return_value = ""

        self.use_case = GetActorDetailToolUseCase(
            actor_repository=self.mock_actor_repository,
            actor_serializer=self.mock_actor_serializer,
            sub_transaction_repository=self.mock_sub_transaction_repository,
            sub_transaction_serializer=self.mock_sub_transaction_serializer,
            user_id=self.user_id,
        )

    def test_execute_returns_string(self):
        """Verify execute() returns a string type."""
        result = self.use_case.execute(
            actor_id="1",
            due_date_start="2026-01-01",
            due_date_end="2026-01-31",
        )
        self.assertIsInstance(result, str)

    def test_execute_does_not_return_dict(self):
        """Verify execute() does not return a dict."""
        result = self.use_case.execute(
            actor_id="1",
            due_date_start="2026-01-01",
            due_date_end="2026-01-31",
        )
        self.assertNotIsInstance(result, dict)


class TestGetActorStatsToolReturnsString(SimpleTestCase):
    """Test that GetActorStatsToolUseCase returns a string."""

    def setUp(self):
        self.mock_actor_stats_use_case = Mock()
        self.user_id = 1

        self.mock_actor_stats_use_case.execute.return_value = {
            "total_spent": 1000.00,
            "biggest_spender": "Test Actor",
            "biggest_spender_amount": 500.00,
            "smallest_spender": "Other Actor",
            "smallest_spender_amount": 100.00,
            "average_spent": 250.00,
            "active_actors": 4,
        }

        self.use_case = GetActorStatsToolUseCase(
            actor_stats_use_case=self.mock_actor_stats_use_case,
            user_id=self.user_id,
        )

    def test_execute_returns_string(self):
        """Verify execute() returns a string type."""
        result = self.use_case.execute(
            due_date_start="2026-01-01",
            due_date_end="2026-01-31",
        )
        self.assertIsInstance(result, str)

    def test_execute_does_not_return_dict(self):
        """Verify execute() does not return a dict."""
        result = self.use_case.execute(
            due_date_start="2026-01-01",
            due_date_end="2026-01-31",
        )
        self.assertNotIsInstance(result, dict)


class TestGetSubTransactionsFromTransactionToolReturnsString(SimpleTestCase):
    """Test that GetSubTransactionsFromTransactionToolUseCase returns a string."""

    def setUp(self):
        self.mock_sub_transaction_serializer = Mock()
        self.mock_sub_transaction_factory = Mock()
        self.mock_sub_transaction_repository = Mock()
        self.mock_transaction_repository = Mock()
        self.user_id = 1

        mock_transaction = Mock()
        mock_transaction.sub_transactions = []
        self.mock_transaction_repository.get.return_value = mock_transaction
        self.mock_sub_transaction_repository.get_all_by_transaction_id.return_value = []
        self.mock_sub_transaction_serializer.serialize_many_for_tool.return_value = ""

        self.use_case = GetSubTransactionsFromTransactionToolUseCase(
            sub_transaction_serializer=self.mock_sub_transaction_serializer,
            sub_transaction_factory=self.mock_sub_transaction_factory,
            sub_transaction_repository=self.mock_sub_transaction_repository,
            transaction_repository=self.mock_transaction_repository,
            user_id=self.user_id,
        )

    def test_execute_returns_string(self):
        """Verify execute() returns a string type."""
        result = self.use_case.execute(transaction_id=1)
        self.assertIsInstance(result, str)

    def test_execute_does_not_return_dict(self):
        """Verify execute() does not return a dict."""
        result = self.use_case.execute(transaction_id=1)
        self.assertNotIsInstance(result, dict)


class TestGetUserGeneralStatsToolReturnsString(SimpleTestCase):
    """Test that GetUserGeneralStatsToolUseCase returns a string."""

    def setUp(self):
        self.mock_transaction_stats_use_case = Mock()
        self.user_id = 1

        self.mock_transaction_stats_use_case.execute.return_value = {
            "incoming_total": 5000.00,
            "outgoing_total": 3000.00,
            "balance": 2000.00,
            "outgoing_from_actors": 1500.00,
        }

        self.use_case = GetUserGeneralStatsToolUseCase(
            transaction_stats_use_case=self.mock_transaction_stats_use_case,
            user_id=self.user_id,
        )

    def test_execute_returns_string(self):
        """Verify execute() returns a string type."""
        result = self.use_case.execute(
            due_date_start="2026-01-01",
            due_date_end="2026-01-31",
        )
        self.assertIsInstance(result, str)

    def test_execute_does_not_return_dict(self):
        """Verify execute() does not return a dict."""
        result = self.use_case.execute(
            due_date_start="2026-01-01",
            due_date_end="2026-01-31",
        )
        self.assertNotIsInstance(result, dict)

    def test_result_is_not_valid_json_object(self):
        """Verify the result is not a JSON object that could be parsed as dict."""
        result = self.use_case.execute(
            due_date_start="2026-01-01",
            due_date_end="2026-01-31",
        )
        try:
            parsed = json.loads(result)
            # If it parses, ensure it's not a dict or list
            self.assertNotIsInstance(parsed, (dict, list))
        except json.JSONDecodeError:
            # Expected - the result should not be valid JSON
            pass

