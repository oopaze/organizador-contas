from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.exceptions import InvalidParamError
from modules.ai.mcp.tools.spending import call_summarize_spending


class TestSummarizeSpendingTool(SimpleTestCase):
    def test_forwards_normalized_filters(self):
        use_case = Mock()
        use_case.execute.return_value = {"total": "100.00", "count": 1, "groups": []}

        result = call_summarize_spending(
            arguments={
                "due_month": "2026-10",
                "purchase_month": "2026-09",
                "category": "transport_fuel",
                "group_by": "category",
            },
            use_case=use_case,
            user_id=7,
        )

        filters = use_case.execute.call_args[0][1]
        self.assertEqual(filters["due_date__year"], 2026)
        self.assertEqual(filters["due_date__month"], 10)
        self.assertEqual(filters["purchase_month"], "2026-09")
        self.assertEqual(filters["category"], "transport_fuel")
        self.assertEqual(filters["transaction_type"], "outgoing")
        self.assertEqual(filters["group_by"], "category")
        self.assertEqual(result["total"], "100.00")

    def test_invalid_group_by_raises(self):
        with self.assertRaises(InvalidParamError):
            call_summarize_spending(
                arguments={"group_by": "planeta"},
                use_case=Mock(),
                user_id=7,
            )
