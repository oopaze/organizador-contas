from django.test import SimpleTestCase

from modules.ai.mcp.factories.enum_listing import EnumListingFactory
from modules.ai.mcp.use_cases.list_enums import ListEnumsUseCase


class TestListEnumsUseCase(SimpleTestCase):
    def setUp(self):
        self.use_case = ListEnumsUseCase(
            enum_listing_factory=EnumListingFactory(),
        )

    def test_returns_transaction_category_and_type(self):
        result = self.use_case.execute()
        self.assertIn("TransactionCategory", result)
        self.assertIn("TransactionType", result)

    def test_transaction_category_has_expected_slugs(self):
        result = self.use_case.execute()
        slugs = [item["slug"] for item in result["TransactionCategory"]]
        self.assertIn("food_grocery", slugs)
        self.assertIn("housing_rent", slugs)

    def test_transaction_type_has_incoming_outgoing(self):
        result = self.use_case.execute()
        slugs = [item["slug"] for item in result["TransactionType"]]
        self.assertEqual(sorted(slugs), ["incoming", "outgoing"])
