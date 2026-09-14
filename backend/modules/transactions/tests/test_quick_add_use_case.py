from unittest.mock import Mock

from django.test import TestCase

from modules.transactions.domains import TransactionDomain
from modules.transactions.use_cases.transaction.quick_add import QuickAddTransactionUseCase


class TestQuickAddTransactionUseCase(TestCase):
    def setUp(self):
        self.transaction_repository = Mock()
        self.transaction_factory = Mock()
        self.transaction_serializer = Mock()
        self.create_sub_transaction_use_case = Mock()
        self.recalculate_amount_use_case = Mock()

        self.use_case = QuickAddTransactionUseCase(
            transaction_repository=self.transaction_repository,
            transaction_factory=self.transaction_factory,
            transaction_serializer=self.transaction_serializer,
            create_sub_transaction_use_case=self.create_sub_transaction_use_case,
            recalculate_amount_use_case=self.recalculate_amount_use_case,
        )

    def test_cash_paid_creates_transaction_and_sub_with_paid_at(self):
        built = TransactionDomain(
            due_date="2026-09-13",
            total_amount="54.90",
            transaction_identifier="Padaria",
            transaction_type="outgoing",
            user_id=7,
            category="food_grocery",
        )
        created = TransactionDomain(
            id=10,
            due_date="2026-09-13",
            total_amount="54.90",
            transaction_identifier="Padaria",
            transaction_type="outgoing",
            user_id=7,
            category="food_grocery",
            paid_at="2026-09-13",
        )
        self.transaction_factory.build.return_value = built
        self.transaction_repository.create.return_value = created
        self.create_sub_transaction_use_case.execute.return_value = {"id": 55}
        self.transaction_serializer.serialize.return_value = {"id": 10}

        result = self.use_case.execute(
            {
                "direction": "outgoing",
                "payment_method": "cash",
                "amount": "54.90",
                "description": "Padaria",
                "date": "2026-09-13",
                "category": "food_grocery",
                "is_paid": True,
            },
            user_id=7,
        )

        built_data = self.transaction_factory.build.call_args[0][0]
        self.assertEqual(built_data["paid_at"], "2026-09-13")
        self.assertEqual(built_data["transaction_identifier"], "Padaria")
        sub_data = self.create_sub_transaction_use_case.execute.call_args[0][0]
        self.assertEqual(sub_data["transaction_id"], 10)
        self.assertEqual(sub_data["paid_at"], "2026-09-13")
        self.assertEqual(sub_data["date"], "2026-09-13")
        self.recalculate_amount_use_case.execute.assert_not_called()
        self.assertEqual(result["sub_transaction_id"], 55)
        self.assertIsNone(result["open_bill_total"])

    def test_cash_scheduled_has_no_paid_at(self):
        created = TransactionDomain(
            id=11, due_date="2026-10-01", total_amount="100", transaction_identifier="Aluguel",
            transaction_type="outgoing", user_id=7, category="housing_rent",
        )
        self.transaction_factory.build.return_value = created
        self.transaction_repository.create.return_value = created
        self.create_sub_transaction_use_case.execute.return_value = {"id": 56}
        self.transaction_serializer.serialize.return_value = {"id": 11}

        self.use_case.execute(
            {
                "direction": "outgoing",
                "payment_method": "cash",
                "amount": "100",
                "description": "Aluguel",
                "date": "2026-10-01",
                "is_paid": False,
            },
            user_id=7,
        )

        built_data = self.transaction_factory.build.call_args[0][0]
        self.assertIsNone(built_data["paid_at"])
        sub_data = self.create_sub_transaction_use_case.execute.call_args[0][0]
        self.assertIsNone(sub_data["paid_at"])

    def test_credit_creates_open_bill_and_recalculates(self):
        open_bill = TransactionDomain(
            id=20, due_date="2026-09-01", total_amount="0", transaction_identifier="Fatura Nubank 09/2026",
            transaction_type="outgoing", user_id=7, category="credit_card",
        )
        filled_bill = TransactionDomain(
            id=20, due_date="2026-09-01", total_amount="54.90", transaction_identifier="Fatura Nubank 09/2026",
            transaction_type="outgoing", user_id=7, category="credit_card",
        )
        self.transaction_repository.get_open_bill.return_value = None
        self.transaction_factory.build.return_value = open_bill
        self.transaction_repository.create.return_value = open_bill
        self.create_sub_transaction_use_case.execute.return_value = {"id": 60}
        self.transaction_repository.get.return_value = filled_bill
        self.transaction_serializer.serialize.return_value = {"id": 20}

        result = self.use_case.execute(
            {
                "payment_method": "credit",
                "amount": "54.90",
                "description": "Padaria",
                "date": "2026-09-13",
                "card_label": "Nubank",
                "is_paid": True,
            },
            user_id=7,
        )

        built_data = self.transaction_factory.build.call_args[0][0]
        self.assertEqual(built_data["transaction_identifier"], "Fatura Nubank 09/2026")
        self.assertEqual(built_data["category"], "credit_card")
        self.assertEqual(built_data["due_date"], "2026-09-01")
        self.assertEqual(built_data["total_amount"], 0)
        sub_data = self.create_sub_transaction_use_case.execute.call_args[0][0]
        self.assertIsNone(sub_data["paid_at"])
        self.recalculate_amount_use_case.execute.assert_called_once_with(20, 7)
        self.assertEqual(result["open_bill_total"], "54.90")

    def test_credit_reuses_existing_open_bill(self):
        existing = TransactionDomain(
            id=21, due_date="2026-09-01", total_amount="100", transaction_identifier="Fatura Nubank 09/2026",
            transaction_type="outgoing", user_id=7, category="credit_card",
        )
        self.transaction_repository.get_open_bill.return_value = existing
        self.create_sub_transaction_use_case.execute.return_value = {"id": 61}
        self.transaction_repository.get.return_value = existing
        self.transaction_serializer.serialize.return_value = {"id": 21}

        self.use_case.execute(
            {
                "payment_method": "credit",
                "amount": "10",
                "description": "Café",
                "date": "2026-09-14",
                "card_label": "nubank ",
            },
            user_id=7,
        )

        self.transaction_factory.build.assert_not_called()
        self.transaction_repository.create.assert_not_called()
        self.transaction_repository.get_open_bill.assert_called_once_with(
            7, "Fatura nubank 09/2026", 2026, 9
        )
        self.recalculate_amount_use_case.execute.assert_called_once_with(21, 7)

    def test_credit_requires_card_label(self):
        with self.assertRaises(ValueError):
            self.use_case.execute(
                {
                    "payment_method": "credit",
                    "amount": "10",
                    "description": "Café",
                    "date": "2026-09-14",
                },
                user_id=7,
            )

    def test_infers_category_when_missing(self):
        infer = Mock()
        infer.execute.return_value = "food_grocery"
        use_case = QuickAddTransactionUseCase(
            transaction_repository=self.transaction_repository,
            transaction_factory=self.transaction_factory,
            transaction_serializer=self.transaction_serializer,
            create_sub_transaction_use_case=self.create_sub_transaction_use_case,
            recalculate_amount_use_case=self.recalculate_amount_use_case,
            infer_category_use_case=infer,
        )
        created = TransactionDomain(
            id=10, due_date="2026-09-13", total_amount="10", transaction_identifier="Padaria",
            transaction_type="outgoing", user_id=7,
        )
        self.transaction_factory.build.return_value = created
        self.transaction_repository.create.return_value = created
        self.create_sub_transaction_use_case.execute.return_value = {"id": 55}
        self.transaction_serializer.serialize.return_value = {"id": 10}

        use_case.execute(
            {
                "direction": "outgoing",
                "payment_method": "cash",
                "amount": "10",
                "description": "Padaria",
                "date": "2026-09-13",
                "is_paid": False,
            },
            user_id=7,
        )

        infer.execute.assert_called_once_with("Padaria", 7)
        built_data = self.transaction_factory.build.call_args[0][0]
        self.assertEqual(built_data["category"], "food_grocery")
        sub_data = self.create_sub_transaction_use_case.execute.call_args[0][0]
        self.assertEqual(sub_data["category"], "food_grocery")

    def test_installments_below_one_raises(self):
        with self.assertRaises(ValueError):
            self.use_case.execute(
                {
                    "direction": "outgoing",
                    "payment_method": "cash",
                    "amount": "100",
                    "description": "Compra",
                    "date": "2026-09-13",
                    "installments": 0,
                },
                user_id=7,
            )

    def test_cash_installments_create_monthly_transactions(self):
        def build_side_effect(data):
            return TransactionDomain(
                due_date=data["due_date"],
                total_amount=data["total_amount"],
                transaction_identifier=data["transaction_identifier"],
                transaction_type=data["transaction_type"],
                user_id=7,
            )

        created_ids = iter([1, 2, 3])

        def create_side_effect(transaction):
            transaction.id = next(created_ids)
            return transaction

        sub_ids = iter([11, 12, 13])
        self.transaction_factory.build.side_effect = build_side_effect
        self.transaction_repository.create.side_effect = create_side_effect
        self.create_sub_transaction_use_case.execute.side_effect = (
            lambda data, user_id: {"id": next(sub_ids)}
        )
        self.transaction_serializer.serialize.return_value = {"id": 1}

        result = self.use_case.execute(
            {
                "direction": "outgoing",
                "payment_method": "cash",
                "amount": "100",
                "description": "Compra parcelada",
                "date": "2026-09-13",
                "installments": 3,
                "is_paid": True,
            },
            user_id=7,
        )

        self.assertEqual(self.transaction_repository.create.call_count, 3)
        parents = [call[0][0] for call in self.transaction_factory.build.call_args_list]
        self.assertEqual([p["paid_at"] for p in parents], ["2026-09-13", None, None])
        self.assertEqual([p["due_date"] for p in parents], ["2026-09-13", "2026-10-13", "2026-11-13"])
        self.assertEqual(parents[1]["main_transaction"], 1)
        self.assertEqual(parents[1]["installment_number"], 2)
        self.assertEqual(parents[2]["recurrence_count"], 3)

        subs = [call[0][0] for call in self.create_sub_transaction_use_case.execute.call_args_list]
        self.assertEqual([s["installment_info"] for s in subs], ["1/3", "2/3", "3/3"])
        self.assertEqual([str(s["amount"]) for s in subs], ["33.33", "33.33", "33.34"])
        self.assertEqual([s["date"] for s in subs], ["2026-09-13", "2026-10-13", "2026-11-13"])
        self.assertEqual(subs[0]["paid_at"], "2026-09-13")
        self.assertIsNone(subs[1]["paid_at"])
        self.assertIsNone(result["open_bill_total"])
        self.assertEqual(result["sub_transaction_id"], 11)

    def test_credit_installments_spread_across_open_bills(self):
        def build_side_effect(data):
            return TransactionDomain(
                due_date=data["due_date"],
                total_amount=data["total_amount"],
                transaction_identifier=data["transaction_identifier"],
                transaction_type=data["transaction_type"],
                user_id=7,
                category="credit_card",
            )

        bills = iter([
            TransactionDomain(id=20, total_amount="0", user_id=7),
            TransactionDomain(id=21, total_amount="0", user_id=7),
            TransactionDomain(id=22, total_amount="0", user_id=7),
        ])

        def create_side_effect(transaction):
            transaction.id = next(bills).id
            return transaction

        sub_ids = iter([31, 32, 33])
        filled_first = TransactionDomain(id=20, total_amount="33.33", user_id=7)
        self.transaction_repository.get_open_bill.return_value = None
        self.transaction_factory.build.side_effect = build_side_effect
        self.transaction_repository.create.side_effect = create_side_effect
        self.transaction_repository.get.return_value = filled_first
        self.create_sub_transaction_use_case.execute.side_effect = (
            lambda data, user_id: {"id": next(sub_ids)}
        )
        self.transaction_serializer.serialize.return_value = {"id": 20}

        result = self.use_case.execute(
            {
                "payment_method": "credit",
                "amount": "100",
                "description": "Compra parcelada",
                "date": "2026-09-13",
                "card_label": "Nubank",
                "installments": 3,
            },
            user_id=7,
        )

        self.assertEqual(
            [call[0][1:] for call in self.transaction_repository.get_open_bill.call_args_list],
            [
                ("Fatura Nubank 09/2026", 2026, 9),
                ("Fatura Nubank 10/2026", 2026, 10),
                ("Fatura Nubank 11/2026", 2026, 11),
            ],
        )
        self.assertEqual(self.transaction_repository.create.call_count, 3)
        self.assertEqual(
            [call[0] for call in self.recalculate_amount_use_case.execute.call_args_list],
            [(20, 7), (21, 7), (22, 7)],
        )
        subs = [call[0][0] for call in self.create_sub_transaction_use_case.execute.call_args_list]
        self.assertEqual([s["installment_info"] for s in subs], ["1/3", "2/3", "3/3"])
        self.assertEqual([s["date"] for s in subs], ["2026-09-13", "2026-10-13", "2026-11-13"])
        self.assertEqual([str(s["amount"]) for s in subs], ["33.33", "33.33", "33.34"])
        self.assertTrue(all(s["paid_at"] is None for s in subs))
        self.assertEqual(result["open_bill_total"], "33.33")
        self.assertEqual(result["sub_transaction_id"], 31)

