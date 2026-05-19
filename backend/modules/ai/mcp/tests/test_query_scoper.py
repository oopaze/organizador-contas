from django.test import SimpleTestCase

from modules.ai.mcp.services.query_scoper import QueryScoperService


class TestQueryScoperService(SimpleTestCase):
    def setUp(self):
        self.service = QueryScoperService()

    def test_wraps_query_with_cte_block(self):
        wrapped, params = self.service.scope(
            "SELECT id FROM transactions_transaction", user_id=42
        )
        self.assertIn("WITH", wrapped.upper())
        self.assertIn("transactions_transaction AS", wrapped)
        self.assertIn("transactions_actor AS", wrapped)
        self.assertIn("transactions_subtransaction AS", wrapped)
        self.assertIn("file_reader_file AS", wrapped)
        self.assertIn("loans_loan AS", wrapped)
        self.assertIn("loans_loanpayment AS", wrapped)

    def test_user_id_is_parameterized(self):
        wrapped, params = self.service.scope(
            "SELECT 1", user_id=42
        )
        self.assertEqual(params, {"user_id": 42})
        # The raw integer must NOT appear in the SQL text
        self.assertNotIn("42", wrapped)

    def test_includes_original_query_at_end(self):
        original = "SELECT id, total_amount FROM transactions_transaction"
        wrapped, _ = self.service.scope(original, user_id=1)
        self.assertTrue(wrapped.rstrip().endswith(original))

    def test_enforces_row_limit_via_outer_wrapper(self):
        wrapped, _ = self.service.scope("SELECT 1", user_id=1, row_limit=1000)
        self.assertIn("LIMIT 1001", wrapped)

    def test_filters_soft_deleted_rows(self):
        wrapped, _ = self.service.scope("SELECT 1", user_id=1)
        # Five tables have deleted_at; file_reader_file does not.
        self.assertEqual(wrapped.count("deleted_at IS NULL"), 5)

    def test_subtransaction_scoped_via_parent_transaction(self):
        wrapped, _ = self.service.scope("SELECT 1", user_id=1)
        self.assertIn("transactions_subtransaction s", wrapped)
        self.assertIn(
            "JOIN public.transactions_transaction t", wrapped
        )

    def test_loan_payment_scoped_via_parent_loan(self):
        wrapped, _ = self.service.scope("SELECT 1", user_id=1)
        self.assertIn("loans_loanpayment p", wrapped)
        self.assertIn("JOIN public.loans_loan l", wrapped)
