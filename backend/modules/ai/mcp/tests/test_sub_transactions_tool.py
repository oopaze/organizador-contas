from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.exceptions import InvalidDateError
from modules.ai.mcp.tools.sub_transactions import call_list_sub_transactions


class TestListSubTransactionsTool(SimpleTestCase):
    def test_builds_filters_and_clamps_limit(self):
        use_case = Mock()
        use_case.execute.return_value = [
            {"id": 1, "category": "Transporte - Combustível"},
            {"id": 2, "category": "Outros"},
        ]

        result = call_list_sub_transactions(
            arguments={
                "purchase_month": "2026-09",
                "due_month": "2026-10",
                "category": "Transporte - Combustível",
                "search": "posto",
                "limit": 1,
            },
            use_case=use_case,
            user_id=7,
        )

        filters = use_case.execute.call_args[1]["filters"]
        self.assertEqual(filters["date__year"], 2026)
        self.assertEqual(filters["date__month"], 9)
        self.assertEqual(filters["transaction__due_date__month"], 10)
        self.assertEqual(filters["category"], "transport_fuel")
        self.assertEqual(filters["description__icontains"], "posto")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["sub_transactions"][0]["category_slug"], "transport_fuel")

    def test_invalid_date_raises(self):
        with self.assertRaises(InvalidDateError):
            call_list_sub_transactions(
                arguments={"purchase_month": "2026-13"},
                use_case=Mock(),
                user_id=7,
            )
