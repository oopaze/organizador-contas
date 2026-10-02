from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.cards.domains.card import CardDomain
from modules.transactions.domains import TransactionDomain
from modules.transactions.use_cases.transaction.get_or_create_card_bill import (
    GetOrCreateCardBillUseCase,
)


class TestGetOrCreateCardBillUseCase(SimpleTestCase):
    def setUp(self):
        self.card_repository = Mock()
        self.transaction_repository = Mock()
        self.transaction_factory = Mock()
        self.use_case = GetOrCreateCardBillUseCase(
            card_repository=self.card_repository,
            transaction_repository=self.transaction_repository,
            transaction_factory=self.transaction_factory,
        )

    def test_returns_existing_bill_without_creating(self):
        self.card_repository.get.return_value = CardDomain(id=3, name="C&A Pay", due_day=5)
        existing = TransactionDomain(
            id=1213,
            transaction_identifier="Fatura C&A Pay 10/2026",
            due_date="2026-10-05",
            user_id=7,
            card_id=3,
        )
        self.transaction_repository.get_bill_by_card.return_value = existing

        result = self.use_case.execute(7, 3, 2026, 10)

        self.assertIs(result, existing)
        self.transaction_repository.get_bill_by_card.assert_called_once_with(7, 3, 2026, 10)
        self.transaction_repository.create.assert_not_called()

    def test_creates_bill_with_card_due_day(self):
        self.card_repository.get.return_value = CardDomain(id=3, name="C&A Pay", due_day=5)
        self.transaction_repository.get_bill_by_card.return_value = None
        built = TransactionDomain(id=1300, user_id=7)
        self.transaction_factory.build.return_value = built
        self.transaction_repository.create.return_value = built

        result = self.use_case.execute(7, 3, 2026, 10)

        self.assertIs(result, built)
        created_data = self.transaction_factory.build.call_args[0][0]
        self.assertEqual(created_data["transaction_identifier"], "Fatura C&A Pay 10/2026")
        self.assertEqual(created_data["due_date"], "2026-10-05")
        self.assertEqual(created_data["card_id"], 3)
        self.assertEqual(created_data["category"], "credit_card")
        self.assertEqual(created_data["total_amount"], 0)
        self.transaction_repository.create.assert_called_once_with(built)

    def test_clamps_due_day_to_month_end(self):
        self.card_repository.get.return_value = CardDomain(id=3, name="Nubank", due_day=31)
        self.transaction_repository.get_bill_by_card.return_value = None
        self.transaction_factory.build.return_value = TransactionDomain(id=1300, user_id=7)
        self.transaction_repository.create.return_value = self.transaction_factory.build.return_value

        self.use_case.execute(7, 3, 2026, 2)

        self.assertEqual(self.transaction_factory.build.call_args[0][0]["due_date"], "2026-02-28")
