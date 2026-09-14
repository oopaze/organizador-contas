from datetime import date
from unittest.mock import Mock

from django.test import TestCase

from modules.cards.domains.card import CardDomain
from modules.transactions.domains import TransactionDomain
from modules.transactions.use_cases.transaction.ensure_card_bills import EnsureMonthlyCardBillsUseCase


class TestEnsureMonthlyCardBillsUseCase(TestCase):
    def setUp(self):
        self.card_repository = Mock()
        self.transaction_repository = Mock()
        self.transaction_factory = Mock()
        self.transaction_serializer = Mock()
        self.recalculate_amount_use_case = Mock()
        self.card_repository.get_for_update.side_effect = (
            lambda card_id, user_id: CardDomain(id=card_id)
        )
        self.use_case = EnsureMonthlyCardBillsUseCase(
            card_repository=self.card_repository,
            transaction_repository=self.transaction_repository,
            transaction_factory=self.transaction_factory,
            transaction_serializer=self.transaction_serializer,
            recalculate_amount_use_case=self.recalculate_amount_use_case,
        )

    def test_creates_zeroed_bill_with_card_due_day(self):
        self.card_repository.get_all.return_value = [CardDomain(id=3, name="Nubank", due_day=10)]
        self.transaction_repository.get_open_bill_by_card.return_value = None
        self.transaction_repository.get_open_bill.return_value = None
        built = TransactionDomain(id=50, total_amount="0", user_id=7)
        self.transaction_factory.build.return_value = built
        self.transaction_repository.create.return_value = built
        self.transaction_repository.get.return_value = built
        self.transaction_serializer.serialize.return_value = {"id": 50}

        result = self.use_case.execute(7, "2026-09")

        self.card_repository.get_all.assert_called_once_with(7, only_active=True)
        self.card_repository.get_for_update.assert_called_once_with(3, 7)
        built_data = self.transaction_factory.build.call_args[0][0]
        self.assertEqual(built_data["transaction_identifier"], "Fatura Nubank 09/2026")
        self.assertEqual(built_data["due_date"], "2026-09-10")
        self.assertEqual(built_data["card_id"], 3)
        self.assertEqual(built_data["category"], "credit_card")
        self.recalculate_amount_use_case.execute.assert_called_once_with(50, 7)
        self.assertEqual(result, {"bills": [{"id": 50}]})

    def test_reuses_existing_bill_and_syncs_due_date(self):
        self.card_repository.get_all.return_value = [CardDomain(id=3, name="Nubank", due_day=10)]
        existing = TransactionDomain(id=50, total_amount="100", user_id=7, due_date=date(2026, 9, 1))
        self.transaction_repository.get_open_bill_by_card.return_value = existing
        self.transaction_repository.update.return_value = existing
        self.transaction_repository.get.return_value = existing
        self.transaction_serializer.serialize.return_value = {"id": 50}

        self.use_case.execute(7, "2026-09")

        self.transaction_repository.create.assert_not_called()
        self.assertEqual(str(existing.due_date), "2026-09-10")
        self.transaction_repository.update.assert_called_once_with(existing)
        self.recalculate_amount_use_case.execute.assert_called_once_with(50, 7)

    def test_does_not_update_when_due_date_already_matches(self):
        self.card_repository.get_all.return_value = [CardDomain(id=3, name="Nubank", due_day=10)]
        existing = TransactionDomain(id=50, total_amount="100", user_id=7, due_date=date(2026, 9, 10))
        self.transaction_repository.get_open_bill_by_card.return_value = existing
        self.transaction_repository.get.return_value = existing
        self.transaction_serializer.serialize.return_value = {"id": 50}

        self.use_case.execute(7, "2026-09")

        self.transaction_repository.create.assert_not_called()
        self.transaction_repository.update.assert_not_called()
        self.recalculate_amount_use_case.execute.assert_called_once_with(50, 7)

    def test_clamps_due_day_to_month_end(self):
        self.card_repository.get_all.return_value = [CardDomain(id=3, name="Nubank", due_day=31)]
        self.transaction_repository.get_open_bill_by_card.return_value = None
        self.transaction_repository.get_open_bill.return_value = None
        built = TransactionDomain(id=50, user_id=7)
        self.transaction_factory.build.return_value = built
        self.transaction_repository.create.return_value = built
        self.transaction_repository.get.return_value = built
        self.transaction_serializer.serialize.return_value = {"id": 50}

        self.use_case.execute(7, "2026-02")

        self.assertEqual(self.transaction_factory.build.call_args[0][0]["due_date"], "2026-02-28")

    def test_adopts_legacy_bill_with_same_identifier(self):
        self.card_repository.get_all.return_value = [CardDomain(id=3, name="Nubank", due_day=10)]
        legacy = TransactionDomain(
            id=60,
            total_amount="100",
            user_id=7,
            due_date=date(2026, 9, 10),
            transaction_identifier="Fatura Nubank 09/2026",
        )
        self.transaction_repository.get_open_bill_by_card.return_value = None
        self.transaction_repository.get_open_bill.return_value = legacy
        self.transaction_repository.update.return_value = legacy
        self.transaction_repository.get.return_value = legacy
        self.transaction_serializer.serialize.return_value = {"id": 60}

        result = self.use_case.execute(7, "2026-09")

        self.transaction_repository.create.assert_not_called()
        self.assertIs(legacy.card_id, 3)
        self.transaction_repository.get_open_bill.assert_called_once_with(
            7, "Fatura Nubank 09/2026", 2026, 9
        )
        self.transaction_repository.update.assert_called_once_with(legacy)
        self.recalculate_amount_use_case.execute.assert_called_once_with(60, 7)
        self.assertEqual(result, {"bills": [{"id": 60}]})
