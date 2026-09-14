import importlib.util
from pathlib import Path

from django.apps import apps as django_apps
from django.test import TestCase
from django.utils import timezone

from modules.cards.models import Card
from modules.file_reader.models import File
from modules.transactions.models import Transaction
from modules.userdata.models import User

MIGRATION_PATH = (
    Path(__file__).resolve().parents[1] / "migrations" / "0017_backfill_cards.py"
)
SPEC = importlib.util.spec_from_file_location("backfill_cards", MIGRATION_PATH)
backfill_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(backfill_module)


class TestBackfillCards(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="backfill@test.com", password="x")
        self.other_user = User.objects.create_user(email="other@test.com", password="x")
        self.file = File.objects.create(raw_file="bill.pdf", user=self.user)

    def make_bill(self, identifier, file=None, user=None):
        return Transaction.objects.create(
            due_date="2026-09-10",
            total_amount="100",
            transaction_identifier=identifier,
            category="credit_card",
            user=user or self.user,
            file=file,
        )

    def run_backfill(self):
        backfill_module.backfill(django_apps, None)

    def test_creates_card_from_open_bill_and_links_it(self):
        bill = self.make_bill("Fatura Nubank 09/2026")

        self.run_backfill()

        bill.refresh_from_db()
        card = Card.objects.get(user=self.user)
        self.assertEqual((card.name, card.due_day, card.is_active), ("Nubank", 1, True))
        self.assertEqual(bill.card_id, card.id)

    def test_reuses_existing_card_ignoring_case_and_extra_spaces(self):
        existing = Card.objects.create(name="nubank", due_day=10, user=self.user)
        bill = self.make_bill("Fatura  Nubank 10/2026")

        self.run_backfill()

        bill.refresh_from_db()
        self.assertEqual(Card.objects.filter(user=self.user).count(), 1)
        self.assertEqual(bill.card_id, existing.id)

    def test_reuses_only_cards_of_same_user(self):
        other_card = Card.objects.create(name="Nubank", due_day=10, user=self.other_user)
        bill = self.make_bill("Fatura Nubank 09/2026")

        self.run_backfill()

        bill.refresh_from_db()
        self.assertNotEqual(bill.card_id, other_card.id)
        self.assertEqual(bill.card.user_id, self.user.id)

    def test_skips_unparseable_and_blank_identifiers(self):
        no_date = self.make_bill("Fatura Nubank")
        blank_name = self.make_bill("Fatura    09/2026")

        self.run_backfill()

        no_date.refresh_from_db()
        blank_name.refresh_from_db()
        self.assertFalse(Card.objects.exists())
        self.assertIsNone(no_date.card_id)
        self.assertIsNone(blank_name.card_id)

    def test_does_not_overwrite_manually_assigned_card(self):
        manual = Card.objects.create(name="Manual", due_day=10, user=self.user)
        bill = self.make_bill("Fatura Nubank 09/2026")
        bill.card = manual
        bill.save(update_fields=["card"])

        self.run_backfill()

        bill.refresh_from_db()
        self.assertEqual(bill.card_id, manual.id)
        self.assertFalse(Card.objects.filter(name="Nubank").exists())

    def test_imported_bill_prefers_longest_matching_card_name(self):
        Card.objects.create(name="Inter", due_day=10, user=self.user)
        longest = Card.objects.create(name="Inter Black", due_day=10, user=self.user)
        bill = self.make_bill("Fatura Inter Black 09/2026", file=self.file)

        self.run_backfill()

        bill.refresh_from_db()
        self.assertEqual(bill.card_id, longest.id)

    def test_imported_bill_links_when_only_short_name_matches(self):
        short = Card.objects.create(name="Inter", due_day=10, user=self.user)
        Card.objects.create(name="Inter Black", due_day=10, user=self.user)
        bill = self.make_bill("Fatura Inter 09/2026", file=self.file)

        self.run_backfill()

        bill.refresh_from_db()
        self.assertEqual(bill.card_id, short.id)

    def test_open_bill_does_not_reuse_soft_deleted_card(self):
        deleted = Card.objects.create(
            name="Nubank", due_day=10, user=self.user, deleted_at=timezone.now()
        )
        bill = self.make_bill("Fatura Nubank 09/2026")

        self.run_backfill()

        bill.refresh_from_db()
        self.assertNotEqual(bill.card_id, deleted.id)
        card = Card.objects.get(user=self.user, deleted_at__isnull=True)
        self.assertEqual(bill.card_id, card.id)

    def test_imported_bill_ignores_soft_deleted_cards(self):
        Card.objects.create(
            name="Nubank", due_day=10, user=self.user, deleted_at=timezone.now()
        )
        bill = self.make_bill("Fatura Nubank 09/2026", file=self.file)

        self.run_backfill()

        bill.refresh_from_db()
        self.assertIsNone(bill.card_id)
        self.assertEqual(Card.objects.filter(user=self.user).count(), 1)
