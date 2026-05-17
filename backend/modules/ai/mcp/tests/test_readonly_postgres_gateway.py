"""Integration tests for ReadOnlyPostgresGateway.

These tests require:
  - psycopg2 installed (use Docker or a venv with psycopg2-binary)
  - The Postgres `poupix_mcp_ro` role created via `make mcp_setup_db`
  - A reachable Postgres instance (db container running)

Enable with environment variable: MCP_PG_INTEGRATION=1
"""
import os

import pytest


if os.environ.get("MCP_PG_INTEGRATION") != "1":
    pytest.skip(
        "Set MCP_PG_INTEGRATION=1 to run gateway integration tests "
        "(requires Postgres + poupix_mcp_ro role).",
        allow_module_level=True,
    )

# Heavy imports only after the skip gate
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase

from modules.ai.mcp.factories.query_result import QueryResultFactory
from modules.ai.mcp.gateways.readonly_postgres import ReadOnlyPostgresGateway
from modules.ai.mcp.domains.sql_query import SqlQuery
from modules.ai.mcp.exceptions import (
    SqlPermissionDeniedError,
    SqlTimeoutError,
    SqlInvalidError,
)
from modules.ai.mcp.services.query_scoper import QueryScoperService
from modules.transactions.models import Transaction


User = get_user_model()


class TestReadOnlyPostgresGateway(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_a = User.objects.create_user(email="a@a.com", password="x")
        cls.user_b = User.objects.create_user(email="b@b.com", password="x")
        Transaction.objects.create(
            user=cls.user_a,
            due_date="2024-01-15",
            total_amount=Decimal("100.00"),
            transaction_identifier="A1",
        )
        Transaction.objects.create(
            user=cls.user_b,
            due_date="2024-01-15",
            total_amount=Decimal("200.00"),
            transaction_identifier="B1",
        )

    def setUp(self):
        self.gateway = ReadOnlyPostgresGateway(
            query_result_factory=QueryResultFactory(),
        )

    def _query(self, raw_sql, user_id):
        wrapped, params = QueryScoperService().scope(raw_sql, user_id=user_id)
        return SqlQuery(raw=raw_sql, wrapped=wrapped, params=params)

    def test_returns_only_users_own_rows(self):
        result = self.gateway.execute(
            self._query("SELECT total_amount FROM transactions_transaction", self.user_a.id)
        )
        amounts = [r[0] for r in result.rows]
        self.assertEqual(amounts, ["100.00"])

    def test_user_b_does_not_see_user_a(self):
        result = self.gateway.execute(
            self._query("SELECT total_amount FROM transactions_transaction", self.user_b.id)
        )
        amounts = [r[0] for r in result.rows]
        self.assertEqual(amounts, ["200.00"])

    def test_insert_is_denied(self):
        with self.assertRaises(SqlPermissionDeniedError):
            self.gateway.execute_raw_for_test(
                "INSERT INTO transactions_transaction (user_id, due_date, "
                "total_amount, transaction_identifier, transaction_type, "
                "is_salary, is_recurrent, category, created_at, updated_at) "
                "VALUES (1, '2024-01-01', 1, 'X', 'outgoing', false, false, "
                "'OTHER', NOW(), NOW())"
            )

    def test_drop_is_denied(self):
        with self.assertRaises(SqlPermissionDeniedError):
            self.gateway.execute_raw_for_test("DROP TABLE transactions_transaction")

    def test_invalid_column_returns_invalid_error(self):
        with self.assertRaises(SqlInvalidError):
            self.gateway.execute(
                self._query("SELECT no_such_column FROM transactions_transaction", self.user_a.id)
            )

    def test_timeout_is_caught(self):
        with self.assertRaises(SqlTimeoutError):
            self.gateway.execute(
                self._query("SELECT pg_sleep(6)", self.user_a.id)
            )
