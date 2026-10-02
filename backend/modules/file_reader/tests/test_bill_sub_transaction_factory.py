from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.file_reader.domains.bill import BillDomain
from modules.file_reader.domains.file import FileDomain
from modules.file_reader.factories.bill_sub_transaction import BillSubTransactionFactory


class TestBillSubTransactionFactory(SimpleTestCase):
    def setUp(self):
        self.factory = BillSubTransactionFactory()
        self.file = Mock(spec=FileDomain)
        self.bill = Mock(spec=BillDomain)
        self.bill.category = "credit_card"

    def build(self, transactions):
        return self.factory.build_many_from_file(
            self.file, self.bill, {"transactions": transactions}
        )

    def test_keeps_purchases(self):
        result = self.build(
            [
                {"date": "2026-09-13", "description": "C&A - SHOPPING CARIRI", "amount": 86.65},
            ]
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].amount, 86.65)

    def test_drops_previous_invoice_payment(self):
        result = self.build(
            [
                {"date": "2026-09-06", "description": "Baixa Pagamento Fatura Via Pix", "amount": -59.99},
                {"date": "2026-09-13", "description": "C&A - SHOPPING CARIRI", "amount": 86.65},
            ]
        )

        self.assertEqual([sub.description for sub in result], ["C&A - SHOPPING CARIRI"])

    def test_drops_payment_received(self):
        result = self.build(
            [
                {"date": "2026-09-08", "description": "PAGAMENTO RECEBIDO - OBRIGADO", "amount": -383.86},
            ]
        )

        self.assertEqual(result, [])

    def test_keeps_legitimate_credits(self):
        transactions = [
            {"date": "2026-09-10", "description": "ESTORNO COMPRA", "amount": -50.0},
            {"date": "2026-09-11", "description": "Pagamento Antecipado", "amount": -100.0},
            {"date": "2026-09-12", "description": "DEVOLUCAO DE COMPRA", "amount": -10.0},
        ]

        result = self.build(transactions)

        self.assertEqual(len(result), 3)

    def test_keeps_negative_without_payment_keywords(self):
        result = self.build(
            [
                {"date": "2026-09-15", "description": "AJUSTE DE SALDO", "amount": -5.0},
            ]
        )

        self.assertEqual(len(result), 1)
