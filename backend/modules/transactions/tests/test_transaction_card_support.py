from datetime import datetime
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.transactions.domains import TransactionDomain
from modules.transactions.factories import TransactionFactory
from modules.transactions.serializers import TransactionSerializer


class TestTransactionCardSupport(SimpleTestCase):
    def test_factory_build_reads_card_id(self):
        factory = TransactionFactory()

        transaction = factory.build(
            {
                "due_date": "2026-09-01",
                "total_amount": "100",
                "transaction_identifier": "Fatura Nubank 09/2026",
                "transaction_type": "outgoing",
                "user_id": 7,
                "category": "credit_card",
                "card_id": 3,
            }
        )

        self.assertEqual(transaction.card_id, 3)

    def test_serializer_includes_card_id(self):
        transaction = TransactionDomain(
            id=1,
            due_date="2026-09-01",
            total_amount="100",
            transaction_identifier="Fatura Nubank 09/2026",
            transaction_type="outgoing",
            user_id=7,
            category="credit_card",
            card_id=3,
            created_at=datetime(2026, 9, 1),
            updated_at=datetime(2026, 9, 1),
        )
        serializer = TransactionSerializer(sub_transaction_serializer=Mock())

        payload = serializer.serialize(transaction)

        self.assertEqual(payload["card_id"], 3)
