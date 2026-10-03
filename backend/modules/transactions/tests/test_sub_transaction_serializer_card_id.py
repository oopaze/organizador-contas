from datetime import datetime
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.transactions.domains import SubTransactionDomain, TransactionDomain
from modules.transactions.serializers import SubTransactionSerializer


class TestSubTransactionSerializerCardId(SimpleTestCase):
    def test_serialize_includes_parent_card_id(self):
        transaction = TransactionDomain(
            id=1,
            due_date="2026-10-08",
            total_amount="100.00",
            transaction_identifier="Fatura Nubank 10/2026",
            transaction_type="outgoing",
            category="credit_card",
            card_id=3,
        )
        sub_transaction = SubTransactionDomain(
            id=10,
            date="2026-09-02",
            description="POSTO PALMEIRAL",
            amount="100.00",
            transaction=transaction,
            category="transport_fuel",
            created_at=datetime(2026, 9, 2),
            updated_at=datetime(2026, 9, 2),
        )

        payload = SubTransactionSerializer(actor_serializer=Mock()).serialize(sub_transaction)

        self.assertEqual(payload["card_id"], 3)
