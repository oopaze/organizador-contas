from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.tools import dispatch_tool, dumps_payload, transactions


class TestDumpsPayload(SimpleTestCase):
    def test_serializes_dates_and_decimals(self):
        text = dumps_payload({"due_date": date(2026, 9, 14), "amount": Decimal("10.50")})

        self.assertIn("2026-09-14", text)
        self.assertIn("10.50", text)


class TestListTransactionsTool(SimpleTestCase):
    def test_builds_user_scoped_filters_and_limit(self):
        use_case = Mock()
        use_case.execute.return_value = [{"id": 1}, {"id": 2}, {"id": 3}]

        result = transactions.call_list_transactions(
            arguments={
                "month": "2026-09",
                "transaction_type": "outgoing",
                "paid": False,
                "search": "padaria",
                "limit": 2,
            },
            use_case=use_case,
            user_id=7,
        )

        filters = use_case.execute.call_args[0][0]
        self.assertEqual(filters["user_id"], 7)
        self.assertEqual(filters["due_date__year"], 2026)
        self.assertEqual(filters["due_date__month"], 9)
        self.assertEqual(filters["transaction_type"], "outgoing")
        self.assertEqual(filters["paid_at__isnull"], True)
        self.assertEqual(filters["transaction_identifier__icontains"], "padaria")
        self.assertEqual(result["transactions"], [{"id": 1}, {"id": 2}])
        self.assertEqual(result["count"], 2)

    def test_range_filters(self):
        use_case = Mock()
        use_case.execute.return_value = []

        transactions.call_list_transactions(
            arguments={"start": "2026-09-01", "end": "2026-09-30"},
            use_case=use_case,
            user_id=7,
        )

        filters = use_case.execute.call_args[0][0]
        self.assertEqual(filters["due_date__gte"], "2026-09-01")
        self.assertEqual(filters["due_date__lte"], "2026-09-30")


class TestGetTransactionTool(SimpleTestCase):
    def test_scopes_by_user(self):
        use_case = Mock()
        use_case.execute.return_value = {"id": 10}

        result = transactions.call_get_transaction(
            arguments={"transaction_id": 10}, use_case=use_case, user_id=7
        )

        use_case.execute.assert_called_once_with(10, 7)
        self.assertEqual(result, {"id": 10})


class TestCreateTransactionTool(SimpleTestCase):
    def test_routes_to_quick_add_when_payment_method_given(self):
        quick_add = Mock()
        quick_add.execute.return_value = {"ok": True}
        use_case = Mock()

        result = transactions.call_create_transaction(
            arguments={
                "transaction_identifier": "Padaria",
                "total_amount": "10",
                "due_date": "2026-09-13",
                "payment_method": "credit",
                "card_label": "Nubank",
                "installments": 3,
                "is_paid": False,
            },
            use_case=use_case,
            quick_add_use_case=quick_add,
            user_id=7,
        )

        data = quick_add.execute.call_args[0][0]
        self.assertEqual(data["payment_method"], "credit")
        self.assertEqual(data["amount"], "10")
        self.assertEqual(data["description"], "Padaria")
        self.assertEqual(data["date"], "2026-09-13")
        self.assertEqual(data["installments"], 3)
        self.assertEqual(data["is_paid"], False)
        use_case.execute.assert_not_called()
        self.assertEqual(result, {"ok": True})

    def test_create_routes_card_id_to_quick_add(self):
        quick_add = Mock()
        quick_add.execute.return_value = {"ok": True}
        transactions.call_create_transaction(
            arguments={
                "transaction_identifier": "Padaria",
                "total_amount": "10",
                "due_date": "2026-09-13",
                "payment_method": "credit",
                "card_id": 3,
            },
            use_case=Mock(),
            quick_add_use_case=quick_add,
            user_id=7,
        )
        data = quick_add.execute.call_args[0][0]
        self.assertEqual(data["card_id"], 3)

    def test_creates_directly_without_payment_method(self):
        use_case = Mock()
        use_case.execute.return_value = {"id": 1}

        transactions.call_create_transaction(
            arguments={
                "transaction_identifier": "Salário",
                "total_amount": "5000",
                "due_date": "2026-09-05",
                "transaction_type": "incoming",
                "is_salary": True,
                "paid_at": "2026-09-05",
            },
            use_case=use_case,
            quick_add_use_case=Mock(),
            user_id=7,
        )

        data = use_case.execute.call_args[0][0]
        self.assertEqual(data["user_id"], 7)
        self.assertEqual(data["transaction_type"], "incoming")
        self.assertTrue(data["is_salary"])
        self.assertEqual(data["paid_at"], "2026-09-05")


class TestUpdateTransactionTool(SimpleTestCase):
    def test_passes_fields_and_user(self):
        use_case = Mock()
        use_case.execute.return_value = {"id": 10}

        transactions.call_update_transaction(
            arguments={"transaction_id": 10, "transaction_identifier": "Novo"},
            use_case=use_case,
            user_id=7,
        )

        transaction_id, data = use_case.execute.call_args[0]
        self.assertEqual(transaction_id, 10)
        self.assertEqual(data["transaction_identifier"], "Novo")
        self.assertEqual(data["user_id"], 7)
        self.assertNotIn("transaction_id", data)


class TestSubTransactionTools(SimpleTestCase):
    def test_create_sub_maps_actor(self):
        use_case = Mock()
        use_case.execute.return_value = {"id": 55}

        transactions.call_create_sub_transaction(
            arguments={
                "transaction_id": 10,
                "description": "Café",
                "amount": "8.50",
                "date": "2026-09-14",
                "actor_id": 3,
            },
            use_case=use_case,
            user_id=7,
        )

        data, user_id = use_case.execute.call_args[0]
        self.assertEqual(data["transaction_id"], 10)
        self.assertEqual(data["actor"], 3)
        self.assertEqual(user_id, 7)

    def test_update_sub_passes_fields(self):
        use_case = Mock()
        use_case.execute.return_value = {"id": 55}

        transactions.call_update_sub_transaction(
            arguments={"sub_transaction_id": 55, "amount": "9.00"},
            use_case=use_case,
            user_id=7,
        )

        sub_id, data, user_id = use_case.execute.call_args[0]
        self.assertEqual(sub_id, 55)
        self.assertEqual(data, {"amount": "9.00"})
        self.assertEqual(user_id, 7)


class TestGetProjectionTool(SimpleTestCase):
    def test_forwards_window_and_months(self):
        use_case = Mock()
        use_case.execute.return_value = {"months": []}

        result = transactions.call_get_projection(
            arguments={"start": "2026-09", "end": "2026-12", "months": 6},
            use_case=use_case,
            user_id=7,
        )

        use_case.execute.assert_called_once_with(7, start="2026-09", end="2026-12", months=6)
        self.assertEqual(result, {"months": []})

    def test_get_projection_includes_goals(self):
        use_case = Mock()
        use_case.execute.return_value = {
            "months": [{"month": "2026-09", "salary": "5000.00"}],
            "total_months": 1,
            "goals": {
                "spending_goal_percent": "3000.00",
                "savings_goal_percent": "1000.00",
                "essentials_goal_percent": "2000.00",
            },
        }

        result = transactions.call_get_projection(
            arguments={"months": 1},
            use_case=use_case,
            user_id=7,
        )

        self.assertIn("goals", result)
        self.assertEqual(result["goals"]["spending_goal_percent"], "3000.00")
        self.assertEqual(result["goals"]["savings_goal_percent"], "1000.00")
        self.assertEqual(result["goals"]["essentials_goal_percent"], "2000.00")


class TestSetGoalsTool(SimpleTestCase):
    def test_updates_only_provided_goals(self):
        profile_repository = Mock()
        profile_repository.get_by_user_id.return_value = Mock(id=42)
        update_use_case = Mock()
        update_use_case.execute.return_value = {"id": 42, "spending_goal_percent": "35.00"}

        result = transactions.call_set_goals(
            arguments={"spending_goal_percent": 35},
            update_profile_use_case=update_use_case,
            profile_repository=profile_repository,
            user_id=7,
        )

        profile_repository.get_by_user_id.assert_called_once_with(7)
        update_use_case.execute.assert_called_once_with(42, {"spending_goal_percent": "35"})
        self.assertEqual(result["spending_goal_percent"], "35.00")

    def test_ignores_none_goals(self):
        profile_repository = Mock()
        profile_repository.get_by_user_id.return_value = Mock(id=42)
        update_use_case = Mock()
        update_use_case.execute.return_value = {}

        transactions.call_set_goals(
            arguments={"savings_goal_percent": None, "essentials_goal_percent": 30},
            update_profile_use_case=update_use_case,
            profile_repository=profile_repository,
            user_id=7,
        )

        update_use_case.execute.assert_called_once_with(42, {"essentials_goal_percent": "30"})


class TestDispatchTool(SimpleTestCase):
    def test_unknown_tool(self):
        result = dispatch_tool("nao_existe", {}, Mock(), user_id=7)

        self.assertEqual(result["error"]["code"], "UNKNOWN_TOOL")

    def test_wraps_use_case_errors(self):
        transaction_use_case = Mock()
        transaction_use_case.execute.side_effect = Exception("boom")
        container = Mock()
        container.transactions_container().list_transactions_use_case.return_value = (
            transaction_use_case
        )

        result = dispatch_tool("list_transactions", {}, container, user_id=7)

        self.assertEqual(result["error"]["code"], "TOOL_ERROR")
        self.assertEqual(result["error"]["message"], "boom")

    def test_routes_list_transactions(self):
        use_case = Mock()
        use_case.execute.return_value = [{"id": 1}]
        container = Mock()
        container.transactions_container().list_transactions_use_case.return_value = (
            use_case
        )

        result = dispatch_tool("list_transactions", {"limit": 1}, container, user_id=7)

        self.assertEqual(result["transactions"], [{"id": 1}])

    def test_routes_get_projection(self):
        use_case = Mock()
        use_case.execute.return_value = {"months": [{"month": "2026-09"}]}
        container = Mock()
        container.planning_container().projection_use_case.return_value = use_case

        result = dispatch_tool("get_projection", {"start": "2026-09"}, container, user_id=7)

        self.assertEqual(result["months"][0]["month"], "2026-09")

    def test_routes_set_goals(self):
        profile_repository = Mock()
        profile_repository.get_by_user_id.return_value = Mock(id=42)
        update_use_case = Mock()
        update_use_case.execute.return_value = {"id": 42}
        container = Mock()
        container.userdata_container().update_profile_use_case.return_value = update_use_case
        container.planning_container().profile_repository.return_value = profile_repository

        result = dispatch_tool(
            "set_goals", {"spending_goal_percent": 30}, container, user_id=7
        )

        self.assertEqual(result["id"], 42)
        update_use_case.execute.assert_called_once_with(42, {"spending_goal_percent": "30"})
