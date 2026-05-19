from django.test import SimpleTestCase

from modules.ai.mcp.factories.table_schema import TableSchemaFactory
from modules.ai.mcp.repositories.schema_introspection import (
    SchemaIntrospectionRepository,
)
from modules.ai.mcp.exceptions import SchemaIntrospectionError


class TestSchemaIntrospectionRepository(SimpleTestCase):
    def setUp(self):
        self.repo = SchemaIntrospectionRepository(
            table_schema_factory=TableSchemaFactory(),
        )

    def test_list_all_returns_all_scoped_tables(self):
        tables = self.repo.list_all()
        names = [t.name for t in tables]
        self.assertEqual(
            sorted(names),
            sorted([
                "transactions_transaction",
                "transactions_subtransaction",
                "transactions_actor",
                "file_reader_file",
                "loans_loan",
                "loans_loanpayment",
            ]),
        )

    def test_get_one_returns_specific_table(self):
        table = self.repo.get("transactions_transaction")
        self.assertEqual(table.name, "transactions_transaction")

    def test_get_unknown_raises(self):
        with self.assertRaises(SchemaIntrospectionError):
            self.repo.get("ai_aicall")
