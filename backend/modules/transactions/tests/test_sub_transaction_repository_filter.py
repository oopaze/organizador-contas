from django.test import TestCase

from modules.transactions.factories import ActorFactory, SubTransactionFactory, TransactionFactory
from modules.transactions.models import SubTransaction, Transaction
from modules.transactions.repositories import SubTransactionRepository
from modules.userdata.models import User


class TestSubTransactionRepositoryFilter(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="subs@test.com", password="x")
        self.repository = SubTransactionRepository(
            model=SubTransaction,
            sub_transaction_factory=SubTransactionFactory(
                transaction_factory=TransactionFactory(), actor_factory=ActorFactory()
            ),
        )
        self.bill = Transaction.objects.create(
            user=self.user,
            due_date="2026-10-08",
            total_amount="300.00",
            transaction_identifier="Fatura Inter 10/2026",
            transaction_type="outgoing",
            category="credit_card",
        )
        SubTransaction.objects.create(
            transaction=self.bill, date="2026-09-02", description="POSTO PALMEIRAL",
            amount="100.00", category="transport_fuel",
        )
        SubTransaction.objects.create(
            transaction=self.bill, date="2026-09-05", description="MERCADINHO",
            amount="200.00", category="food_grocery",
        )

    def test_filters_by_purchase_month_and_category(self):
        result = self.repository.filter(
            self.user.id,
            {"date__year": 2026, "date__month": 9, "category": "transport_fuel"},
        )

        self.assertEqual([sub.description for sub in result], ["POSTO PALMEIRAL"])

    def test_filters_by_parent_due_month_and_search(self):
        result = self.repository.filter(
            self.user.id,
            {"transaction__due_date__month": 10, "description__icontains": "merc"},
        )

        self.assertEqual([sub.description for sub in result], ["MERCADINHO"])
