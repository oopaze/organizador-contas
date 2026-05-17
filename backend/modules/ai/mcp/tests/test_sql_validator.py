from django.test import SimpleTestCase

from modules.ai.mcp.services.sql_validator import SqlValidatorService
from modules.ai.mcp.exceptions import (
    SqlNotAllowedError,
    SqlMultipleStatementsError,
)


class TestSqlValidatorService(SimpleTestCase):
    def setUp(self):
        self.service = SqlValidatorService()

    def test_accepts_simple_select(self):
        result = self.service.validate("SELECT 1")
        self.assertEqual(result.strip(), "SELECT 1")

    def test_accepts_select_with_table(self):
        result = self.service.validate(
            "SELECT id, total_amount FROM transactions_transaction WHERE due_date > '2024-01-01'"
        )
        self.assertIn("SELECT", result.upper())

    def test_accepts_with_clause(self):
        result = self.service.validate(
            "WITH x AS (SELECT 1 AS id) SELECT * FROM x"
        )
        self.assertIn("WITH", result.upper())

    def test_strips_trailing_semicolon(self):
        result = self.service.validate("SELECT 1;")
        self.assertFalse(result.strip().endswith(";"))

    def test_rejects_insert(self):
        with self.assertRaises(SqlNotAllowedError):
            self.service.validate("INSERT INTO transactions_transaction (id) VALUES (1)")

    def test_rejects_update(self):
        with self.assertRaises(SqlNotAllowedError):
            self.service.validate("UPDATE transactions_transaction SET total_amount = 0")

    def test_rejects_delete(self):
        with self.assertRaises(SqlNotAllowedError):
            self.service.validate("DELETE FROM transactions_transaction")

    def test_rejects_drop(self):
        with self.assertRaises(SqlNotAllowedError):
            self.service.validate("DROP TABLE transactions_transaction")

    def test_rejects_truncate(self):
        with self.assertRaises(SqlNotAllowedError):
            self.service.validate("TRUNCATE transactions_transaction")

    def test_rejects_alter(self):
        with self.assertRaises(SqlNotAllowedError):
            self.service.validate("ALTER TABLE transactions_transaction ADD COLUMN x int")

    def test_rejects_grant(self):
        with self.assertRaises(SqlNotAllowedError):
            self.service.validate("GRANT ALL ON transactions_transaction TO public")

    def test_rejects_multiple_statements(self):
        with self.assertRaises(SqlMultipleStatementsError):
            self.service.validate("SELECT 1; SELECT 2")

    def test_rejects_empty_query(self):
        with self.assertRaises(SqlNotAllowedError):
            self.service.validate("")

    def test_rejects_whitespace_only(self):
        with self.assertRaises(SqlNotAllowedError):
            self.service.validate("   \n  ")

    def test_strips_line_comments(self):
        result = self.service.validate("SELECT 1 -- evil comment\n")
        self.assertNotIn("--", result)

    def test_strips_block_comments(self):
        result = self.service.validate("SELECT /* evil */ 1")
        self.assertNotIn("/*", result)
