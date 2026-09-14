from unittest.mock import Mock

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from modules.transactions.domains import ActorDomain, SubTransactionDomain, TransactionDomain
from modules.transactions.use_cases.transaction.apply_reconciliation import (
    ApplyReconciliationUseCase,
)


class TestApplyReconciliationUseCase(TestCase):
    def setUp(self):
        self.transaction_repository = Mock()
        self.sub_transaction_repository = Mock()
        self.recalculate_amount_use_case = Mock()
        self.use_case = ApplyReconciliationUseCase(
            transaction_repository=self.transaction_repository,
            sub_transaction_repository=self.sub_transaction_repository,
            recalculate_amount_use_case=self.recalculate_amount_use_case,
        )
        self.open_bill = TransactionDomain(
            id=20, due_date="2026-09-01", total_amount="100",
            transaction_identifier="Fatura Nubank 09/2026", transaction_type="outgoing",
            user_id=7, category="credit_card",
        )
        self.bill = TransactionDomain(
            id=50, due_date="2026-09-20", total_amount="100",
            transaction_identifier="Nubank", transaction_type="outgoing",
            user_id=7, category="credit_card", file_id=99,
        )
        self.actor = ActorDomain(id=3, name="Amor")
        self.bill_sub = SubTransactionDomain(
            id=101, transaction=self.bill, date="2026-09-03", amount="100",
            description="PADARIA", category="food_grocery",
        )
        self.real_sub = SubTransactionDomain(
            id=40, transaction=self.open_bill, date="2026-09-03", amount="100",
            description="Padaria", category="other", actor=self.actor,
        )
        self.real_sub.user_provided_description = "com amor"

        def get_sub(sub_id, user_id):
            return {101: self.bill_sub, 40: self.real_sub}[sub_id]

        self.sub_transaction_repository.get.side_effect = get_sub
        self.sub_transaction_repository.get_all_by_transaction_id.return_value = []
        self.transaction_repository.get.return_value = self.open_bill

    def test_merges_pair_and_closes_empty_open_bill(self):
        result = self.use_case.execute(
            {"pairs": [{"bill_sub_transaction_id": 101, "real_sub_transaction_id": 40}]},
            user_id=7,
        )

        self.assertEqual(self.bill_sub.actor.id, 3)
        self.assertEqual(self.bill_sub.user_provided_description, "com amor")
        self.sub_transaction_repository.update.assert_any_call(self.bill_sub)
        self.sub_transaction_repository.delete.assert_called_once_with(40)
        self.transaction_repository.delete.assert_called_once_with(20, 7)
        self.recalculate_amount_use_case.execute.assert_not_called()
        self.assertEqual(result["merged"], 1)
        self.assertEqual(result["closed_open_bills"], [20])

    def test_keeps_open_bill_when_unmatched_subs_remain(self):
        remaining = SubTransactionDomain(
            id=41, transaction=self.open_bill, date="2026-09-04", amount="10",
            description="Café", category="other",
        )
        self.sub_transaction_repository.get.side_effect = None
        self.sub_transaction_repository.get.return_value = self.real_sub
        self.sub_transaction_repository.get_all_by_transaction_id.return_value = [remaining]

        result = self.use_case.execute(
            {"pairs": [{"bill_sub_transaction_id": 101, "real_sub_transaction_id": 40}]},
            user_id=7,
        )

        self.recalculate_amount_use_case.execute.assert_called_once_with(20, 7)
        self.transaction_repository.delete.assert_not_called()
        self.assertEqual(result["closed_open_bills"], [])

    def test_skips_already_applied_pairs(self):
        self.sub_transaction_repository.get.side_effect = ObjectDoesNotExist

        result = self.use_case.execute(
            {"pairs": [{"bill_sub_transaction_id": 101, "real_sub_transaction_id": 40}]},
            user_id=7,
        )

        self.sub_transaction_repository.delete.assert_not_called()
        self.assertEqual(result["merged"], 0)

    def test_applies_categories(self):
        self.sub_transaction_repository.get.side_effect = lambda sub_id, user_id: {
            101: self.bill_sub, 40: self.real_sub,
        }[sub_id]
        self.sub_transaction_repository.get_all_by_transaction_id.return_value = []

        result = self.use_case.execute(
            {
                "pairs": [{"bill_sub_transaction_id": 101, "real_sub_transaction_id": 40}],
                "categories": [{"sub_transaction_id": 101, "category": "food_restaurant"}],
            },
            user_id=7,
        )

        self.assertEqual(result["categorized"], 1)
