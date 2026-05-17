from django.test import SimpleTestCase

from modules.ai.mcp.factories.table_schema import TableSchemaFactory
from modules.transactions.models import Transaction


class TestTableSchemaFactory(SimpleTestCase):
    def setUp(self):
        self.factory = TableSchemaFactory()

    def test_extracts_table_name(self):
        schema = self.factory.from_django_model(Transaction)
        self.assertEqual(schema.name, "transactions_transaction")

    def test_extracts_description(self):
        schema = self.factory.from_django_model(Transaction)
        self.assertIn("Transação principal", schema.description)

    def test_extracts_columns_with_pk(self):
        schema = self.factory.from_django_model(Transaction)
        names = [c.name for c in schema.columns]
        self.assertIn("id", names)
        id_col = next(c for c in schema.columns if c.name == "id")
        self.assertTrue(id_col.pk)

    def test_extracts_indexed_columns(self):
        schema = self.factory.from_django_model(Transaction)
        due_date = next(c for c in schema.columns if c.name == "due_date")
        self.assertTrue(due_date.indexed)

    def test_extracts_foreign_keys(self):
        schema = self.factory.from_django_model(Transaction)
        main = next(
            (c for c in schema.columns if c.name == "main_transaction_id"),
            None,
        )
        self.assertIsNotNone(main)
        self.assertEqual(main.fk, "transactions_transaction.id")

    def test_includes_column_notes_from_docs(self):
        schema = self.factory.from_django_model(Transaction)
        main = next(c for c in schema.columns if c.name == "main_transaction_id")
        self.assertIn("parcelas", main.notes)

    def test_extracts_enum_ref_for_category(self):
        schema = self.factory.from_django_model(Transaction)
        cat = next(c for c in schema.columns if c.name == "category")
        self.assertEqual(cat.enum_ref, "TransactionCategory")

    def test_extracts_relationships(self):
        schema = self.factory.from_django_model(Transaction)
        joined = " ".join(schema.relationships)
        self.assertIn("transactions_subtransaction", joined)
