from django.test import TestCase
from django.utils import timezone

from modules.cards.models import Card
from modules.file_reader.models import File
from modules.transactions.factories import TransactionFactory
from modules.transactions.models import Transaction
from modules.transactions.repositories import TransactionRepository
from modules.userdata.models import User


class TestCardBillLookup(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="lookup@test.com", password="x")
        self.other_user = User.objects.create_user(email="other@test.com", password="x")
        self.card = Card.objects.create(name="C&A Pay", due_day=5, user=self.user)
        self.other_card = Card.objects.create(name="Nubank", due_day=5, user=self.user)
        self.file = File.objects.create(raw_file="bill.pdf", user=self.user)
        self.repository = TransactionRepository(
            model=Transaction, transaction_factory=TransactionFactory()
        )

    def make_bill(self, identifier, due_date="2026-10-05", card=None, user=None, file=None, **extra):
        return Transaction.objects.create(
            due_date=due_date,
            total_amount="86.65",
            transaction_identifier=identifier,
            category="credit_card",
            user=user or self.user,
            card=card or self.card,
            file=file,
            **extra,
        )

    def test_finds_imported_bill_by_card_and_month(self):
        imported = self.make_bill("C&A Pay", file=self.file)

        found = self.repository.get_bill_by_card(self.user.id, self.card.id, 2026, 10)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, imported.id)

    def test_prefers_open_bill_when_both_exist(self):
        self.make_bill("C&A Pay", file=self.file)
        open_bill = self.make_bill("Fatura C&A Pay 10/2026")

        found = self.repository.get_bill_by_card(self.user.id, self.card.id, 2026, 10)

        self.assertEqual(found.id, open_bill.id)

    def test_is_scoped_to_user_and_card(self):
        self.make_bill("C&A Pay", card=self.other_card, file=self.file)
        self.make_bill("C&A Pay", user=self.other_user, file=self.file)

        found = self.repository.get_bill_by_card(self.user.id, self.card.id, 2026, 10)

        self.assertIsNone(found)

    def test_ignores_soft_deleted_bill(self):
        self.make_bill("C&A Pay", file=self.file, deleted_at=timezone.now())

        found = self.repository.get_bill_by_card(self.user.id, self.card.id, 2026, 10)

        self.assertIsNone(found)

    def test_attach_file_marks_monthly_bill_as_imported(self):
        open_bill = self.make_bill("Fatura C&A Pay 10/2026")

        self.repository.attach_file(open_bill.id, self.user.id, self.file.id)

        open_bill.refresh_from_db()
        self.assertEqual(open_bill.file_id, self.file.id)

    def test_attach_file_is_scoped_to_user(self):
        open_bill = self.make_bill("Fatura C&A Pay 10/2026")

        self.repository.attach_file(open_bill.id, self.other_user.id, self.file.id)

        open_bill.refresh_from_db()
        self.assertIsNone(open_bill.file_id)
