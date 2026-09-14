from unittest.mock import Mock

from django.test import TestCase

from modules.transactions.domains import SubTransactionDomain, TransactionDomain
from modules.transactions.use_cases.transaction.ledger import LedgerUseCase


class TestLedgerUseCase(TestCase):
    def setUp(self):
        self.transaction_repository = Mock()
        self.sub_transaction_repository = Mock()
        self.use_case = LedgerUseCase(
            transaction_repository=self.transaction_repository,
            sub_transaction_repository=self.sub_transaction_repository,
        )

    def _sub(self, id, transaction, date, amount, paid_at=None, description="compra"):
        return SubTransactionDomain(
            id=id, transaction=transaction, date=date, amount=amount,
            description=description, paid_at=paid_at,
        )

    def test_counts_subs_for_transactions_with_subs_and_parent_for_salary(self):
        bill = TransactionDomain(
            id=1, due_date="2026-09-10", total_amount="100", transaction_identifier="Fatura Nubank 09/2026",
            transaction_type="outgoing", user_id=7, category="credit_card",
        )
        salary = TransactionDomain(
            id=2, due_date="2026-09-05", total_amount="5000", transaction_identifier="Salário",
            transaction_type="incoming", user_id=7, category="income", paid_at="2026-09-05",
        )
        purchase = self._sub(10, bill, "2026-09-03", "100", paid_at=None)

        self.transaction_repository.filter.return_value = [bill, salary]
        self.sub_transaction_repository.get_all_by_transaction_ids.return_value = [purchase]
        self.sub_transaction_repository.get_by_date_range.return_value = [purchase]

        result = self.use_case.execute(7, start="2026-09-01", end="2026-09-30")
        entries = result["entries"]

        identifiers = [entry["transaction_identifier"] for entry in entries]
        self.assertIn("Salário", identifiers)
        bill_entries = [entry for entry in entries if entry["transaction_id"] == 1]
        self.assertEqual(len(bill_entries), 1)
        self.assertEqual(bill_entries[0]["sub_transaction_id"], 10)
        purchase_entry = next(e for e in entries if e["sub_transaction_id"] == 10)
        self.assertEqual(purchase_entry["direction"], "outgoing")
        self.assertTrue(purchase_entry["is_card"])
        self.assertEqual(result["summary"]["projected_balance"], "4900.00")
        self.assertEqual(result["summary"]["realized_balance"], "5000.00")
        self.assertEqual(result["summary"]["payable"], "100.00")

    def test_running_balance_is_chronological(self):
        income = TransactionDomain(
            id=1, due_date="2026-09-01", total_amount="100", transaction_identifier="Pix recebido",
            transaction_type="incoming", user_id=7, category="income", paid_at="2026-09-01",
        )
        expense = TransactionDomain(
            id=2, due_date="2026-09-02", total_amount="30", transaction_identifier="Padaria",
            transaction_type="outgoing", user_id=7, category="food", paid_at="2026-09-02",
        )
        self.transaction_repository.filter.return_value = [expense, income]
        self.sub_transaction_repository.get_all_by_transaction_ids.return_value = []
        self.sub_transaction_repository.get_by_date_range.return_value = []

        result = self.use_case.execute(7, start="2026-09-01", end="2026-09-30")

        self.assertEqual(
            [entry["running_balance"] for entry in result["entries"]],
            ["100.00", "70.00"],
        )

    def test_include_unpaid_false_removes_unpaid_entries(self):
        paid = TransactionDomain(
            id=1, due_date="2026-09-01", total_amount="100", transaction_identifier="Pago",
            transaction_type="outgoing", user_id=7, category="other", paid_at="2026-09-01",
        )
        unpaid = TransactionDomain(
            id=2, due_date="2026-09-02", total_amount="30", transaction_identifier="Previsto",
            transaction_type="outgoing", user_id=7, category="other",
        )
        self.transaction_repository.filter.return_value = [paid, unpaid]
        self.sub_transaction_repository.get_all_by_transaction_ids.return_value = []
        self.sub_transaction_repository.get_by_date_range.return_value = []

        result = self.use_case.execute(7, include_unpaid=False)

        self.assertEqual(len(result["entries"]), 1)
        self.assertEqual(result["entries"][0]["transaction_identifier"], "Pago")
