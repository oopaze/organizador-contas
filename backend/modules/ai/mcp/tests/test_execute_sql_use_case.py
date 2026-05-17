from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.domains.query_result import QueryResult
from modules.ai.mcp.domains.sql_query import SqlQuery
from modules.ai.mcp.exceptions import SqlNotAllowedError
from modules.ai.mcp.use_cases.execute_sql import ExecuteSqlUseCase


class TestExecuteSqlUseCase(SimpleTestCase):
    def setUp(self):
        self.mock_factory = Mock()
        self.mock_gateway = Mock()
        self.use_case = ExecuteSqlUseCase(
            sql_query_factory=self.mock_factory,
            readonly_postgres_gateway=self.mock_gateway,
        )

    def test_passes_query_through_factory_then_gateway(self):
        sql_query = SqlQuery(raw="SELECT 1", wrapped="WITH ... SELECT 1", params={"user_id": 7})
        expected = QueryResult(
            columns=["?column?"], rows=[[1]], row_count=1,
            truncated=False, execution_ms=5,
        )
        self.mock_factory.from_raw.return_value = sql_query
        self.mock_gateway.execute.return_value = expected

        result = self.use_case.execute("SELECT 1", user_id=7)

        self.mock_factory.from_raw.assert_called_once_with("SELECT 1", user_id=7)
        self.mock_gateway.execute.assert_called_once_with(sql_query)
        self.assertEqual(result, expected)

    def test_propagates_validator_errors(self):
        self.mock_factory.from_raw.side_effect = SqlNotAllowedError("nope")
        with self.assertRaises(SqlNotAllowedError):
            self.use_case.execute("DROP TABLE x", user_id=1)
        self.mock_gateway.execute.assert_not_called()
