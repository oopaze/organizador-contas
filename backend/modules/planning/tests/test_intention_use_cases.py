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
        self.assertEqual(filters["month__year"], 2026)
        self.assertEqual(filters["month__month"], 9)
        self.assertEqual(result, [{"id": 1}])

    def test_status_filter(self):
        repository = Mock()
        serializer = Mock()
        repository.filter.return_value = []

        use_case = ListPurchaseIntentionsUseCase(repository, serializer)
        use_case.execute(7, status="planned")

        filters = repository.filter.call_args[0][0]
        self.assertEqual(filters["status"], "planned")


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


class TestDeletePurchaseIntentionUseCase(SimpleTestCase):
    def test_soft_deletes_scoped_to_user(self):
        repository = Mock()

        use_case = DeletePurchaseIntentionUseCase(repository)
        result = use_case.execute(1, user_id=7)

        repository.delete.assert_called_once_with(1, 7)
        self.assertEqual(result, {"message": "success"})


class TestConvertPurchaseIntentionUseCase(SimpleTestCase):
    def test_creates_transaction_and_marks_bought(self):
        repository = Mock()
        serializer = Mock()
        transactions_container = Mock()
        transaction_use_case = Mock()
        transactions_container.create_transaction_use_case.return_value = transaction_use_case
        transaction_use_case.execute.return_value = {"id": 42}

        intention = PurchaseIntentionDomain(
            id=1, name="Notebook", amount="3500", month=date(2026, 10, 1), user_id=7
        )
        repository.get.return_value = intention
        repository.update.return_value = intention
        serializer.serialize.return_value = {"id": 1, "status": "bought", "transaction_id": 42}

        use_case = ConvertPurchaseIntentionUseCase(repository, serializer, transactions_container)
        result = use_case.execute(1, {"category": "personal_shopping"}, user_id=7)

        repository.get.assert_called_once_with(1, 7)
        transaction_data = transaction_use_case.execute.call_args[0][0]
        self.assertEqual(transaction_data["transaction_identifier"], "Notebook")
        self.assertEqual(transaction_data["total_amount"], "3500")
        self.assertEqual(transaction_data["due_date"], "2026-10-01")
        self.assertEqual(transaction_data["transaction_type"], "outgoing")
        self.assertEqual(transaction_data["category"], "personal_shopping")
        self.assertEqual(transaction_data["user_id"], 7)
        self.assertIsNone(transaction_data["paid_at"])

        self.assertEqual(intention.status, "bought")
        self.assertEqual(intention.transaction_id, 42)
        repository.update.assert_called_once_with(intention)
        self.assertEqual(result["transaction_id"], 42)
