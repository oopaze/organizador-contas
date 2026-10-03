from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.transactions.domains import SubTransactionDomain, TransactionDomain
from modules.transactions.use_cases.transaction.summarize_spending import SummarizeSpendingUseCase


def build_use_case(transactions, sub_transactions, cards=None):
    transaction_repository = Mock()
    transaction_repository.filter.return_value = transactions
    sub_transaction_repository = Mock()
    sub_transaction_repository.get_all_by_transaction_ids.return_value = sub_transactions
    card_repository = Mock()
    card_repository.get_all.return_value = cards or []
    return SummarizeSpendingUseCase(
        transaction_repository=transaction_repository,
        sub_transaction_repository=sub_transaction_repository,
        card_repository=card_repository,
    )


def build_bill_with_subs():
    bill = TransactionDomain(
        id=1, due_date=date(2026, 10, 8), total_amount=Decimal("500.00"),
        transaction_identifier="Fatura Nubank 10/2026", transaction_type="outgoing",
        category="credit_card", card_id=1, user_id=7,
    )
    fuel = SubTransactionDomain(
        id=1, date=date(2026, 9, 2), description="POSTO", amount=Decimal("100.00"),
        transaction=bill, category="transport_fuel",
    )
    market = SubTransactionDomain(
        id=2, date=date(2026, 9, 5), description="MERCADO", amount=Decimal("400.00"),
        transaction=bill, category="food_grocery",
    )
    return bill, fuel, market


class TestSummarizeSpendingUseCase(SimpleTestCase):
    def test_card_bill_counts_subs_not_total(self):
        bill, fuel, market = build_bill_with_subs()
        use_case = build_use_case([bill], [fuel, market])

        result = use_case.execute(7, {"transaction_type": "outgoing"})

        self.assertEqual(result["total"], "500.00")
        self.assertEqual(result["count"], 2)

    def test_category_filter_does_not_leak_bill_total(self):
        bill, fuel, market = build_bill_with_subs()
        use_case = build_use_case([bill], [fuel, market])

        result = use_case.execute(7, {"category": "transport_fuel"})

        self.assertEqual(result["total"], "100.00")
        self.assertEqual(result["count"], 1)

    def test_standalone_transaction_counts_total_and_uses_due_date(self):
        pix = TransactionDomain(
            id=2, due_date=date(2026, 9, 20), total_amount=Decimal("50.00"),
            transaction_identifier="Posto via Pix", transaction_type="outgoing",
            category="transport_fuel", user_id=7,
        )
        use_case = build_use_case([pix], [])

        result = use_case.execute(7, {"purchase_month": "2026-09"})

        self.assertEqual(result["total"], "50.00")
        self.assertEqual(result["count"], 1)

    def test_group_by_category(self):
        bill, fuel, market = build_bill_with_subs()
        use_case = build_use_case([bill], [fuel, market])

        result = use_case.execute(7, {"group_by": "category"})

        groups = {group["key"]: group for group in result["groups"]}
        self.assertEqual(groups["food_grocery"]["total"], "400.00")
        self.assertEqual(groups["transport_fuel"]["label"], "Transporte - Combustível")

    def test_group_by_card(self):
        card = Mock(id=1)
        card.name = "Nubank"
        bill, fuel, market = build_bill_with_subs()
        use_case = build_use_case([bill], [fuel, market], cards=[card])

        result = use_case.execute(7, {"group_by": "card"})

        self.assertEqual(result["groups"][0]["label"], "Nubank")

    def test_group_by_month(self):
        bill, fuel, market = build_bill_with_subs()
        use_case = build_use_case([bill], [fuel, market])

        result = use_case.execute(7, {"group_by": "month"})

        self.assertEqual(result["groups"][0]["key"], "2026-09")
