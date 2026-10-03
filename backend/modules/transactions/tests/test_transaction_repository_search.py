from django.test import TestCase

from modules.transactions.factories import TransactionFactory
from modules.transactions.models import SubTransaction, Transaction
from modules.transactions.repositories import TransactionRepository
from modules.userdata.models import User


class TestTransactionRepositorySearch(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="search@test.com", password="x")
        self.repository = TransactionRepository(
            model=Transaction, transaction_factory=TransactionFactory()
        )
        self.bill = Transaction.objects.create(
            user=self.user,
            due_date="2026-10-08",
            total_amount="500.00",
            transaction_identifier="Fatura Nubank 10/2026",
            transaction_type="outgoing",
            category="credit_card",
        )
        SubTransaction.objects.create(
            transaction=self.bill,
            date="2026-09-02",
            description="POSTO PALMEIRAL",
            amount="100.00",
            category="transport_fuel",
        )
        SubTransaction.objects.create(
            transaction=self.bill,
            date="2026-09-05",
            description="POSTO PALMEIRAL",
            amount="100.00",
            category="transport_fuel",
        )

    def test_search_matches_sub_description_once(self):
        result = self.repository.filter({"user_id": self.user.id, "search": "posto"})

        self.assertEqual([transaction.id for transaction in result], [self.bill.id])

    def test_search_still_matches_identifier(self):
        result = self.repository.filter({"user_id": self.user.id, "search": "nubank"})

        self.assertEqual([transaction.id for transaction in result], [self.bill.id])
