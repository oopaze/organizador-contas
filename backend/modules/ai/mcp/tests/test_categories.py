from django.test import SimpleTestCase

from modules.ai.mcp.categories import enrich_transaction, resolve_category, with_category_slug
from modules.ai.mcp.exceptions import InvalidCategoryError


class TestResolveCategory(SimpleTestCase):
    def test_accepts_slug(self):
        self.assertEqual(resolve_category("transport_fuel"), "transport_fuel")

    def test_accepts_label(self):
        self.assertEqual(resolve_category("Transporte - Combustível"), "transport_fuel")

    def test_none_passthrough(self):
        self.assertIsNone(resolve_category(None))

    def test_invalid_raises_actionable_error(self):
        with self.assertRaises(InvalidCategoryError) as ctx:
            resolve_category("nao_existe")

        self.assertEqual(ctx.exception.code, "INVALID_CATEGORY")
        self.assertIn("list_enums", str(ctx.exception))


class TestEnrichCategorySlug(SimpleTestCase):
    def test_adds_slug_from_label(self):
        data = {"category": "Transporte - Combustível"}
        self.assertEqual(with_category_slug(data)["category_slug"], "transport_fuel")

    def test_unknown_label_becomes_none(self):
        self.assertEqual(with_category_slug({"category": "Nada"})["category_slug"], None)

    def test_enriches_transaction_and_subs(self):
        data = {
            "category": "Cartão de Crédito",
            "sub_transactions": [{"category": "Transporte - Combustível"}],
        }
        enriched = enrich_transaction(data)
        self.assertEqual(enriched["category_slug"], "credit_card")
        self.assertEqual(enriched["sub_transactions"][0]["category_slug"], "transport_fuel")
