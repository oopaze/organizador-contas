from datetime import date
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.planning.domains.intention import PurchaseIntentionDomain
from modules.planning.use_cases.intention.convert import ConvertPurchaseIntentionUseCase
from modules.planning.use_cases.intention.create import CreatePurchaseIntentionUseCase
from modules.planning.use_cases.intention.delete import DeletePurchaseIntentionUseCase
from modules.planning.use_cases.intention.list import ListPurchaseIntentionsUseCase
from modules.planning.use_cases.intention.update import UpdatePurchaseIntentionUseCase


class TestCreatePurchaseIntentionUseCase(SimpleTestCase):
    def test_builds_with_user_and_serializes(self):
        repository = Mock()
        factory = Mock()
        serializer = Mock()
        factory.build.return_value = PurchaseIntentionDomain(
            name="Notebook", amount="3500", month="2026-10-01", user_id=7
        )
        repository.create.return_value = PurchaseIntentionDomain(
            id=1, name="Notebook", amount="3500", month="2026-10-01", user_id=7
        )
        serializer.serialize.return_value = {"id": 1}

        use_case = CreatePurchaseIntentionUseCase(repository, factory, serializer)
        result = use_case.execute(
            {"name": "Notebook", "amount": "3500", "month": "2026-10-01"}, user_id=7
        )

        built = factory.build.call_args[0][0]
        self.assertEqual(built["user_id"], 7)
        self.assertEqual(built["name"], "Notebook")
        self.assertEqual(result, {"id": 1})


class TestListPurchaseIntentionsUseCase(SimpleTestCase):
    def test_month_filter_is_user_scoped(self):
        repository = Mock()
        serializer = Mock()
        repository.filter.return_value = [PurchaseIntentionDomain(id=1, month=date(2026, 9, 1))]
        serializer.serialize.return_value = {"id": 1}

        use_case = ListPurchaseIntentionsUseCase(repository, serializer)
        result = use_case.execute(7, month="2026-09")

        filters = repository.filter.call_args[0][0]
        self.assertEqual(filters["user_id"], 7)
        self.assertEqual(filters["month__lte"], "2026-09-30")
        self.assertEqual(result, [{"id": 1}])

    def test_status_filter(self):
        repository = Mock()
        serializer = Mock()
        repository.filter.return_value = []

        use_case = ListPurchaseIntentionsUseCase(repository, serializer)
        use_case.execute(7, status="planned")

        filters = repository.filter.call_args[0][0]
        self.assertEqual(filters["status"], "planned")

    def test_includes_installments_from_previous_months(self):
        repository = Mock()
        serializer = Mock()
        repository.filter.return_value = [
            PurchaseIntentionDomain(id=1, month=date(2026, 9, 1), installments=6),
            PurchaseIntentionDomain(id=2, month=date(2026, 9, 1), installments=2),
            PurchaseIntentionDomain(id=3, month=date(2026, 5, 1), installments=3),
            PurchaseIntentionDomain(id=4, month=date(2026, 11, 1), installments=1, status="bought"),
        ]
        serializer.serialize.side_effect = lambda domain: {"id": domain.id}

        use_case = ListPurchaseIntentionsUseCase(repository, serializer)
        result = use_case.execute(7, month="2026-11")

        self.assertEqual([item["id"] for item in result], [1, 4])
        self.assertEqual(result[0]["carry_over"], True)
        self.assertNotIn("carry_over", result[1])

    def test_range_includes_planned_carry_over_from_before_start(self):
        repository = Mock()
        serializer = Mock()
        repository.filter.return_value = [
            PurchaseIntentionDomain(
                id=1, name="Celular", amount="5000", month=date(2026, 8, 1),
                installments=10, status="planned",
            ),
        ]
        serializer.serialize.side_effect = lambda domain: {"id": domain.id}

        use_case = ListPurchaseIntentionsUseCase(repository, serializer)
        result = use_case.execute(7, start="2026-09", end="2026-10")

        self.assertEqual(result, [{"id": 1, "carry_over": True}])
        filters = repository.filter.call_args[0][0]
        self.assertNotIn("month__gte", filters)

    def test_range_excludes_carry_over_past_last_installment(self):
        repository = Mock()
        serializer = Mock()
        repository.filter.return_value = [
            PurchaseIntentionDomain(
                id=1, month=date(2026, 6, 1), installments=2, status="planned",
            ),
        ]
        serializer.serialize.side_effect = lambda domain: {"id": domain.id}

        use_case = ListPurchaseIntentionsUseCase(repository, serializer)
        result = use_case.execute(7, start="2026-09", end="2026-10")

        self.assertEqual(result, [])

    def test_range_excludes_bought_carry_over(self):
        repository = Mock()
        serializer = Mock()
        repository.filter.return_value = [
            PurchaseIntentionDomain(
                id=1, month=date(2026, 8, 1), installments=10, status="bought",
            ),
        ]
        serializer.serialize.side_effect = lambda domain: {"id": domain.id}

        use_case = ListPurchaseIntentionsUseCase(repository, serializer)
        result = use_case.execute(7, start="2026-09", end="2026-10")

        self.assertEqual(result, [])


class TestUpdatePurchaseIntentionUseCase(SimpleTestCase):
    def test_updates_and_serializes(self):
        repository = Mock()
        serializer = Mock()
        intention = PurchaseIntentionDomain(id=1, name="Antigo", user_id=7)
        repository.get.return_value = intention
        repository.update.return_value = intention
        serializer.serialize.return_value = {"id": 1}

        use_case = UpdatePurchaseIntentionUseCase(repository, serializer)
        result = use_case.execute(1, {"name": "Novo", "amount": "10"}, user_id=7)

        repository.get.assert_called_once_with(1, 7)
        self.assertEqual(intention.name, "Novo")
        repository.update.assert_called_once_with(intention)
        self.assertEqual(result, {"id": 1})

    def test_refuses_status_change_after_bought(self):
        repository = Mock()
        intention = PurchaseIntentionDomain(id=1, status="bought", user_id=7)
        repository.get.return_value = intention

        use_case = UpdatePurchaseIntentionUseCase(repository, Mock())
        with self.assertRaises(ValueError):
            use_case.execute(1, {"status": "dismissed"}, user_id=7)

        repository.update.assert_not_called()


class TestDeletePurchaseIntentionUseCase(SimpleTestCase):
    def test_soft_deletes_planned_intention(self):
        repository = Mock()
        repository.get.return_value = PurchaseIntentionDomain(id=1, status="planned", user_id=7)

        use_case = DeletePurchaseIntentionUseCase(repository)
        result = use_case.execute(1, user_id=7)

        repository.delete.assert_called_once_with(1, 7)
        self.assertEqual(result, {"message": "success"})

    def test_refuses_to_delete_bought_intention(self):
        repository = Mock()
        repository.get.return_value = PurchaseIntentionDomain(id=1, status="bought", user_id=7)

        use_case = DeletePurchaseIntentionUseCase(repository)
        with self.assertRaises(ValueError):
            use_case.execute(1, user_id=7)

        repository.delete.assert_not_called()


class TestConvertPurchaseIntentionUseCase(SimpleTestCase):
    def test_creates_installments_and_marks_bought(self):
        repository = Mock()
        serializer = Mock()
        transactions_container = Mock()
        quick_add = Mock()
        transactions_container.quick_add_transaction_use_case.return_value = quick_add
        quick_add.execute.return_value = {
            "transaction": {"id": 42},
            "sub_transaction_id": 1,
            "open_bill_total": None,
        }

        intention = PurchaseIntentionDomain(
            id=1, name="Notebook", amount="3500", month=date(2026, 10, 1),
            installments=4, user_id=7,
        )
        repository.get.return_value = intention
        repository.update.return_value = intention
        serializer.serialize.return_value = {"id": 1, "status": "bought", "transaction_id": 42}

        use_case = ConvertPurchaseIntentionUseCase(repository, serializer, transactions_container)
        result = use_case.execute(1, {"category": "personal_shopping"}, user_id=7)

        repository.get.assert_called_once_with(1, 7)
        data = quick_add.execute.call_args[0][0]
        self.assertEqual(data["payment_method"], "cash")
        self.assertEqual(data["amount"], "3500")
        self.assertEqual(data["description"], "Notebook")
        self.assertEqual(data["date"], "2026-10-01")
        self.assertEqual(data["installments"], 4)
        self.assertFalse(data["is_paid"])
        self.assertEqual(data["category"], "personal_shopping")

        self.assertEqual(intention.status, "bought")
        self.assertEqual(intention.transaction_id, 42)
        repository.update.assert_called_once_with(intention)
        self.assertEqual(result["transaction_id"], 42)

    def test_refuses_already_converted(self):
        repository = Mock()
        repository.get.return_value = PurchaseIntentionDomain(id=1, status="bought", user_id=7)

        use_case = ConvertPurchaseIntentionUseCase(repository, Mock(), Mock())
        with self.assertRaises(ValueError):
            use_case.execute(1, {}, user_id=7)
