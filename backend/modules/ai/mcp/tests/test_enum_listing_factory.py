from django.test import SimpleTestCase

from modules.ai.mcp.factories.enum_listing import EnumListingFactory
from modules.transactions.types import TransactionCategory


class TestEnumListingFactory(SimpleTestCase):
    def setUp(self):
        self.factory = EnumListingFactory()

    def test_builds_from_basetype(self):
        listing = self.factory.from_basetype("TransactionCategory", TransactionCategory)
        self.assertEqual(listing.name, "TransactionCategory")
        slugs = [v.slug for v in listing.values]
        self.assertIn("food_grocery", slugs)
        self.assertIn("housing_rent", slugs)
        self.assertIn("other", slugs)

    def test_labels_are_portuguese(self):
        listing = self.factory.from_basetype("TransactionCategory", TransactionCategory)
        food_grocery = next(v for v in listing.values if v.slug == "food_grocery")
        self.assertEqual(food_grocery.label, "Alimentação - Mercado")

    def test_builds_from_choices(self):
        listing = self.factory.from_choices(
            "TransactionType",
            [("incoming", "Incoming"), ("outgoing", "Outgoing")],
        )
        self.assertEqual(listing.name, "TransactionType")
        self.assertEqual([v.slug for v in listing.values], ["incoming", "outgoing"])
