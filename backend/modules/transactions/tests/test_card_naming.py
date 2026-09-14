from django.test import SimpleTestCase

from modules.transactions.services.card_naming import parse_open_bill_identifier


class TestParseOpenBillIdentifier(SimpleTestCase):
    def test_parses_name_month_year(self):
        self.assertEqual(parse_open_bill_identifier("Fatura Nubank 09/2026"), ("Nubank", 9, 2026))

    def test_parses_multi_word_name(self):
        self.assertEqual(
            parse_open_bill_identifier("Fatura C&A Pay 12/2025"), ("C&A Pay", 12, 2025)
        )

    def test_rejects_other_identifiers(self):
        self.assertIsNone(parse_open_bill_identifier("Nubank"))
        self.assertIsNone(parse_open_bill_identifier("Fatura Nubank"))
