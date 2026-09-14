from datetime import date
from unittest.mock import Mock

from django.test import TestCase

from modules.transactions.domains import SubTransactionDomain, TransactionDomain
from modules.transactions.use_cases.transaction.reconcile_bill_preview import (
    ReconcileBillPreviewUseCase,
)


class TestReconcileBillPreviewUseCase(TestCase):
    def setUp(self):
        self.transaction_repository = Mock()
        self.sub_transaction_repository = Mock()
        self.ai_call_repository = Mock()
        self.ask_use_case = Mock()
        self.use_case = ReconcileBillPreviewUseCase(
            transaction_repository=self.transaction_repository,
            sub_transaction_repository=self.sub_transaction_repository,
            ai_call_repository=self.ai_call_repository,
            ask_use_case=self.ask_use_case,
        )
        self.bill = TransactionDomain(
            id=50, due_date=date(2026, 9, 20), total_amount="100",
            transaction_identifier="Nubank", transaction_type="outgoing",
            user_id=7, category="credit_card", file_id=99,
        )
        self.open_bill = TransactionDomain(
            id=20, due_date=date(2026, 9, 1), total_amount="100",
            transaction_identifier="Fatura Nubank 09/2026", transaction_type="outgoing",
            user_id=7, category="credit_card",
        )
        self.bill_sub = SubTransactionDomain(
            id=101, transaction=self.bill, date=date(2026, 9, 3), amount="100",
            description="PADARIA SAO JOSE", category="food_grocery",
        )
        self.real_sub = SubTransactionDomain(
            id=40, transaction=self.open_bill, date=date(2026, 9, 3), amount="100",
            description="Padaria", category="other",
        )
        self.transaction_repository.get.return_value = self.bill
        self.transaction_repository.get_open_bills.return_value = [self.open_bill]
        self.sub_transaction_repository.get_all_by_transaction_id.return_value = [self.bill_sub]
        self.sub_transaction_repository.get_all_by_transaction_ids.return_value = [self.real_sub]
        self.ask_use_case.execute.return_value = 1
        ai_call = Mock()
        ai_call.response = {
            "pairs": [
                {"bill_sub_transaction_id": 101, "real_sub_transaction_id": 40, "confidence": 0.95, "reason": "valor e data"}
            ],
            "categories": [{"sub_transaction_id": 101, "category": "food_grocery"}],
            "unmatched_bill_sub_transaction_ids": [],
            "unmatched_real_sub_transaction_ids": [],
        }
        self.ai_call_repository.get.return_value = ai_call

    def test_builds_preview_with_validated_pairs(self):
        result = self.use_case.execute(50, user_id=7)

        self.assertEqual(len(result["pairs"]), 1)
        self.assertEqual(result["pairs"][0]["real_sub_transaction_id"], 40)
        self.assertEqual(result["pairs"][0]["real_transaction_id"], 20)
        self.assertEqual(result["unmatched_bill"], [])
        self.assertEqual(result["suggested_categories"], [{"sub_transaction_id": 101, "category": "food_grocery"}])

    def test_filters_candidates_by_bill_card(self):
        self.bill.card_id = 3
        other_bill = TransactionDomain(
            id=21, due_date=date(2026, 9, 1), total_amount="50",
            transaction_identifier="Fatura Visa 09/2026", transaction_type="outgoing",
            user_id=7, category="credit_card", card_id=9,
        )
        self.open_bill.card_id = 3
        self.transaction_repository.get_open_bills.return_value = [self.open_bill, other_bill]

        self.use_case.execute(50, user_id=7)

        self.sub_transaction_repository.get_all_by_transaction_ids.assert_called_once_with([20])

    def test_drops_pairs_with_invalid_ids(self):
        self.ai_call_repository.get.return_value.response = {
            "pairs": [{"bill_sub_transaction_id": 999, "real_sub_transaction_id": 40, "confidence": 0.9}],
            "categories": [],
            "unmatched_bill_sub_transaction_ids": [101],
            "unmatched_real_sub_transaction_ids": [40],
        }

        result = self.use_case.execute(50, user_id=7)

        self.assertEqual(result["pairs"], [])
        self.assertEqual(len(result["unmatched_bill"]), 1)
        self.assertEqual(len(result["unmatched_real"]), 1)

    def test_rejects_non_credit_card_bill(self):
        self.transaction_repository.get.return_value = TransactionDomain(
            id=50, due_date="2026-09-20", total_amount="100",
            transaction_identifier="Luz", transaction_type="outgoing",
            user_id=7, category="bill_electricity",
        )

        with self.assertRaises(ValueError):
            self.use_case.execute(50, user_id=7)
