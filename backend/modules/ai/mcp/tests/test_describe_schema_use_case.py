from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.domains.table_schema import ColumnSchema, TableSchema
from modules.ai.mcp.use_cases.describe_schema import DescribeSchemaUseCase


class TestDescribeSchemaUseCase(SimpleTestCase):
    def setUp(self):
        self.mock_repo = Mock()
        self.use_case = DescribeSchemaUseCase(
            schema_introspection_repository=self.mock_repo,
        )

    def test_execute_without_table_returns_all(self):
        t1 = TableSchema(name="a", description="A", columns=[])
        t2 = TableSchema(name="b", description="B", columns=[])
        self.mock_repo.list_all.return_value = [t1, t2]

        result = self.use_case.execute(table=None)

        self.assertEqual(result, {"tables": [t1.to_dict(), t2.to_dict()]})
        self.mock_repo.list_all.assert_called_once()
        self.mock_repo.get.assert_not_called()

    def test_execute_with_table_returns_one(self):
        t = TableSchema(
            name="a", description="A",
            columns=[ColumnSchema(name="id", type="bigint", pk=True)],
        )
        self.mock_repo.get.return_value = t

        result = self.use_case.execute(table="a")

        self.assertEqual(result, t.to_dict())
        self.mock_repo.get.assert_called_once_with("a")
