from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.factories.query_result import QueryResultFactory


class TestQueryResultFactory(SimpleTestCase):
    def setUp(self):
        self.factory = QueryResultFactory()

    def _mock_cursor(self, description, rows):
        cursor = Mock()
        cursor.description = [(name,) for name in description]
        cursor.fetchall.return_value = rows
        return cursor

    def test_builds_result_from_cursor(self):
        cursor = self._mock_cursor(
            ["id", "total_amount"],
            [(1, Decimal("10.50")), (2, Decimal("20.00"))],
        )
        result = self.factory.from_cursor(
            cursor, started_at_ms=0, row_limit=1000, now_ms=42
        )
        self.assertEqual(result.columns, ["id", "total_amount"])
        self.assertEqual(result.rows, [[1, "10.50"], [2, "20.00"]])
        self.assertEqual(result.row_count, 2)
        self.assertFalse(result.truncated)
        self.assertEqual(result.execution_ms, 42)

    def test_truncates_at_row_limit(self):
        rows = [(i,) for i in range(1001)]
        cursor = self._mock_cursor(["id"], rows)
        result = self.factory.from_cursor(
            cursor, started_at_ms=0, row_limit=1000, now_ms=10
        )
        self.assertEqual(result.row_count, 1000)
        self.assertTrue(result.truncated)
        self.assertEqual(len(result.rows), 1000)

    def test_converts_date_to_iso(self):
        cursor = self._mock_cursor(
            ["due_date"], [(date(2024, 3, 15),)]
        )
        result = self.factory.from_cursor(
            cursor, started_at_ms=0, row_limit=1000, now_ms=0
        )
        self.assertEqual(result.rows[0][0], "2024-03-15")

    def test_converts_datetime_to_iso(self):
        cursor = self._mock_cursor(
            ["created_at"],
            [(datetime(2024, 3, 15, 12, 30, tzinfo=timezone.utc),)],
        )
        result = self.factory.from_cursor(
            cursor, started_at_ms=0, row_limit=1000, now_ms=0
        )
        self.assertTrue(result.rows[0][0].startswith("2024-03-15T12:30:00"))
