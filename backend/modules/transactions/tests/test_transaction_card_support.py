from datetime import datetime
from unittest.mock import Mock

from django.test import SimpleTestCase, TestCase

from modules.cards.models import Card
from modules.transactions.domains import TransactionDomain
from modules.transactions.factories import TransactionFactory
from modules.transactions.models import Transaction
from modules.transactions.repositories import TransactionRepository
from modules.transactions.serializers import TransactionSerializer
from modules.userdata.models import User


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


class TestTransactionCardPersistence(TestCase):
    def test_card_id_survives_create_and_update(self):
        user = User.objects.create_user(email="cards@test.com", password="x")
        card = Card.objects.create(name="Nubank", due_day=10, user=user)
        other_card = Card.objects.create(name="Inter", due_day=15, user=user)
        repository = TransactionRepository(
            model=Transaction, transaction_factory=TransactionFactory()
        )
        transaction = TransactionFactory().build(
            {
                "due_date": "2026-09-01",
                "total_amount": "0",
                "transaction_identifier": "Fatura Nubank 09/2026",
                "transaction_type": "outgoing",
                "user_id": user.id,
                "category": "credit_card",
                "card_id": card.id,
            }
        )

        created = repository.create(transaction)

        self.assertEqual(created.card_id, card.id)
        self.assertEqual(Transaction.objects.get(id=created.id).card_id, card.id)

        created.card_id = other_card.id
        updated = repository.update(created)

        self.assertEqual(updated.card_id, other_card.id)
        self.assertEqual(Transaction.objects.get(id=created.id).card_id, other_card.id)
