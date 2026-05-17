from django.test import SimpleTestCase

from modules.ai.mcp.factories.sql_query import SqlQueryFactory
from modules.ai.mcp.services.sql_validator import SqlValidatorService
from modules.ai.mcp.services.query_scoper import QueryScoperService
from modules.ai.mcp.exceptions import SqlNotAllowedError


class TestSqlQueryFactory(SimpleTestCase):
    def setUp(self):
        self.factory = SqlQueryFactory(
            sql_validator=SqlValidatorService(),
            query_scoper=QueryScoperService(),
        )

    def test_builds_sql_query_from_valid_select(self):
        result = self.factory.from_raw(
            "SELECT id FROM transactions_transaction", user_id=42
        )
        self.assertEqual(
            result.raw, "SELECT id FROM transactions_transaction"
        )
        self.assertIn("WITH", result.wrapped.upper())
        self.assertEqual(result.params, {"user_id": 42})

    def test_propagates_validator_errors(self):
        with self.assertRaises(SqlNotAllowedError):
            self.factory.from_raw("DROP TABLE x", user_id=1)
