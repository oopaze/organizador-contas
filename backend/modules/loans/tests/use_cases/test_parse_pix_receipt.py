from decimal import Decimal
from datetime import date
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.loans.use_cases.parse_pix_receipt import ParsePixReceiptUseCase


class TestParsePixReceiptUseCase(SimpleTestCase):
    def setUp(self):
        self.ask = Mock()
        self.ai_call_repo = Mock()
        self.use_case = ParsePixReceiptUseCase(
            ask_use_case=self.ask,
            ai_call_repository=self.ai_call_repo,
        )

    def _stub_response(self, payload):
        ai_call_id = "call-123"
        ai_call = Mock()
        ai_call.response = payload
        self.ask.execute.return_value = ai_call_id
        self.ai_call_repo.get.return_value = ai_call
        return ai_call_id

    def test_parses_valid_response(self):
        self._stub_response({
            "amount": 1000.00,
            "paid_at": "2026-03-15",
            "payer_name": "Amor",
            "payee_name": "Pedro",
            "transaction_id": "E12345",
            "bank": "Banco Inter",
        })

        result = self.use_case.execute(raw_text="...", file_name="comprovante.pdf", user_id=7, model="gemini-2.5-flash-lite")

        self.assertEqual(result["amount"], Decimal("1000.00"))
        self.assertEqual(result["paid_at"], date(2026, 3, 15))
        self.assertEqual(result["payer_name"], "Amor")
        self.assertEqual(result["transaction_id"], "E12345")

    def test_raises_when_amount_missing(self):
        self._stub_response({"amount": None, "paid_at": "2026-03-15"})
        with self.assertRaises(ValueError):
            self.use_case.execute(raw_text="...", file_name="x.pdf", user_id=7, model="gemini-2.5-flash-lite")

    def test_raises_when_paid_at_missing(self):
        self._stub_response({"amount": 1000.00, "paid_at": None})
        with self.assertRaises(ValueError):
            self.use_case.execute(raw_text="...", file_name="x.pdf", user_id=7, model="gemini-2.5-flash-lite")

    def test_handles_malformed_date(self):
        self._stub_response({"amount": 1000.00, "paid_at": "not-a-date"})
        with self.assertRaises(ValueError):
            self.use_case.execute(raw_text="...", file_name="x.pdf", user_id=7, model="gemini-2.5-flash-lite")
