from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from modules.transactions.container import TransactionsContainer
from modules.transactions.models import SubTransaction, Transaction
from modules.userdata.models import User


class TestSummarizeSpendingQueries(TestCase):
    def test_query_count_does_not_grow_per_subtransaction(self):
        user = User.objects.create_user(email="queries@test.com", password="x")
        bill = Transaction.objects.create(
            user=user,
            due_date="2026-10-08",
            total_amount="500.00",
            transaction_identifier="Fatura Nubank 10/2026",
            transaction_type="outgoing",
            category="credit_card",
        )
        for index in range(8):
            SubTransaction.objects.create(
                transaction=bill,
                date="2026-09-02",
                description=f"COMPRA {index}",
                amount="10.00",
                category="other",
            )
        use_case = TransactionsContainer().summarize_spending_use_case()

        with CaptureQueriesContext(connection) as first_run:
            use_case.execute(user.id, {})

        for index in range(8, 16):
            SubTransaction.objects.create(
                transaction=bill,
                date="2026-09-02",
                description=f"COMPRA {index}",
                amount="10.00",
                category="other",
            )

        with CaptureQueriesContext(connection) as second_run:
            result = use_case.execute(user.id, {})

        self.assertEqual(len(first_run), len(second_run))
        self.assertEqual(result["count"], 16)
        self.assertEqual(result["total"], "160.00")
