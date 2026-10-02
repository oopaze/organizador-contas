"""End-to-end (DB) tests for importing a card bill: it must feed the monthly bill."""

from decimal import Decimal

from django.test import TestCase

from modules.ai.models import AICall
from modules.cards.factories import CardFactory
from modules.cards.models import Card
from modules.cards.repositories import CardRepository
from modules.file_reader.factories.ai_call import AICallFactory
from modules.file_reader.factories.bill import BillFactory
from modules.file_reader.factories.bill_sub_transaction import BillSubTransactionFactory
from modules.file_reader.factories.file import FileFactory
from modules.file_reader.models import File
from modules.file_reader.repositories.bill import BillRepository
from modules.file_reader.repositories.bill_sub_transaction import BillSubTransactionRepository
from modules.file_reader.repositories.file import FileRepository
from modules.file_reader.serializers.bill import BillSerializer
from modules.file_reader.serializers.bill_sub_transaction import BillSubTransactionSerializer
from modules.file_reader.use_cases.transpose_file_bill_to_models import (
    TransposeFileBillToModelsUseCase,
)
from modules.transactions.factories import ActorFactory, SubTransactionFactory, TransactionFactory
from modules.transactions.models import SubTransaction, Transaction
from modules.transactions.repositories import SubTransactionRepository, TransactionRepository
from modules.transactions.serializers import (
    ActorSerializer,
    SubTransactionSerializer,
    TransactionSerializer,
)
from modules.transactions.use_cases.transaction.apply_reconciliation import (
    ApplyReconciliationUseCase,
)
from modules.transactions.use_cases.transaction.ensure_card_bills import (
    EnsureMonthlyCardBillsUseCase,
)
from modules.transactions.use_cases.transaction.get_or_create_card_bill import (
    GetOrCreateCardBillUseCase,
)
from modules.transactions.use_cases.transaction.recalculate_amount import RecalculateAmountUseCase
from modules.userdata.models import User


class TestImportFeedsMonthlyCardBill(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="import@test.com", password="x")
        self.card = Card.objects.create(name="C&A Pay", due_day=5, user=self.user)

        transaction_factory = TransactionFactory()
        actor_factory = ActorFactory()
        self.transaction_repository = TransactionRepository(
            model=Transaction, transaction_factory=transaction_factory
        )
        sub_transaction_factory = SubTransactionFactory(
            transaction_factory=transaction_factory, actor_factory=actor_factory
        )
        self.sub_transaction_repository = SubTransactionRepository(
            model=SubTransaction, sub_transaction_factory=sub_transaction_factory
        )
        self.recalculate = RecalculateAmountUseCase(
            transaction_repository=self.transaction_repository,
            sub_transaction_repository=self.sub_transaction_repository,
        )

        card_repository = CardRepository(model=Card, card_factory=CardFactory())
        self.get_or_create_card_bill = GetOrCreateCardBillUseCase(
            card_repository=card_repository,
            transaction_repository=self.transaction_repository,
            transaction_factory=transaction_factory,
        )

        ai_call_factory = AICallFactory()
        file_factory = FileFactory(ai_call_factory=ai_call_factory)
        bill_factory = BillFactory(file_factory=file_factory)
        bill_sub_transaction_factory = BillSubTransactionFactory()

        self.transpose = TransposeFileBillToModelsUseCase(
            bill_repository=BillRepository(model=Transaction, bill_factory=bill_factory),
            bill_factory=bill_factory,
            bill_serializer=BillSerializer(BillSubTransactionSerializer()),
            bill_sub_transaction_repository=BillSubTransactionRepository(
                model=SubTransaction, bill_sub_transaction_factory=bill_sub_transaction_factory
            ),
            bill_sub_transaction_factory=bill_sub_transaction_factory,
            file_repository=FileRepository(model=File, file_factory=file_factory),
            recalculate_amount_use_case=self.recalculate,
            get_or_create_card_bill_use_case=self.get_or_create_card_bill,
            transaction_repository=self.transaction_repository,
            sub_transaction_repository=self.sub_transaction_repository,
        )
        self.ensure_bills = EnsureMonthlyCardBillsUseCase(
            card_repository=card_repository,
            transaction_repository=self.transaction_repository,
            transaction_factory=transaction_factory,
            transaction_serializer=TransactionSerializer(
                sub_transaction_serializer=SubTransactionSerializer(actor_serializer=ActorSerializer())
            ),
            recalculate_amount_use_case=self.recalculate,
        )
        self.apply_reconciliation = ApplyReconciliationUseCase(
            transaction_repository=self.transaction_repository,
            sub_transaction_repository=self.sub_transaction_repository,
            recalculate_amount_use_case=self.recalculate,
            get_or_create_card_bill_use_case=self.get_or_create_card_bill,
        )

    def make_file(self, response):
        ai_call = AICall.objects.create(
            prompt=[],
            response=response,
            model="test",
            total_tokens=1,
            input_used_tokens=1,
            output_used_tokens=1,
            user=self.user,
        )
        return File.objects.create(raw_file="ca-pay.pdf", user=self.user, ai_call=ai_call)

    def test_upload_with_card_creates_one_monthly_bill_per_month(self):
        file = self.make_file(
            {
                "bill_identifier": "C&A Pay",
                "total_amount": 146.64,
                "due_date": "2026-10-05",
                "transactions": [
                    {
                        "date": "2026-09-13",
                        "description": "C&A - SHOPPING CARIRI",
                        "amount": 86.65,
                        "installment_info": "1/5",
                        "category": "lifestyle",
                    },
                    {
                        "date": "2026-07-12",
                        "description": "C&A - SHOPPING CARIRI",
                        "amount": 59.99,
                        "installment_info": "3/4",
                        "category": "lifestyle",
                    },
                ],
            }
        )
        self.ensure_bills.execute(self.user.id, "2026-10")
        monthly_bill = self.transaction_repository.get_bill_by_card(
            self.user.id, self.card.id, 2026, 10
        )

        created_ids = self.transpose.execute(
            str(file.id), self.user.id, create_in_future_months=True, card_id=self.card.id
        )

        self.assertEqual(created_ids[0], monthly_bill.id)
        bills = Transaction.objects.filter(
            user=self.user, card=self.card, category="credit_card", deleted_at__isnull=True
        ).order_by("due_date")
        self.assertEqual(bills.count(), 5)
        self.assertTrue(all(bill.transaction_identifier.startswith("Fatura C&A Pay") for bill in bills))
        self.assertFalse(Transaction.objects.filter(user=self.user, transaction_identifier="C&A Pay").exists())

        monthly_bill_instance = bills.get(due_date="2026-10-05")
        self.assertEqual(monthly_bill_instance.file_id, file.id)
        self.assertEqual(monthly_bill_instance.total_amount, Decimal("146.64"))
        self.assertEqual(
            len(
                self.sub_transaction_repository.get_all_by_transaction_id(
                    monthly_bill_instance.id, self.user.id
                )
            ),
            2,
        )

    def test_import_absorbs_shell_into_monthly_bill_with_launches(self):
        file = self.make_file(
            {
                "bill_identifier": "C&A Pay",
                "total_amount": 10.00,
                "due_date": "2026-11-05",
                "transactions": [
                    {
                        "date": "2026-10-20",
                        "description": "C&A - SHOPPING CARIRI",
                        "amount": 10.00,
                        "installment_info": "",
                        "category": "lifestyle",
                    },
                ],
            }
        )
        self.ensure_bills.execute(self.user.id, "2026-11")
        monthly_bill = self.transaction_repository.get_bill_by_card(
            self.user.id, self.card.id, 2026, 11
        )
        SubTransaction.objects.create(
            date="2026-10-15",
            description="Compra no tempo real",
            amount=30,
            transaction_id=monthly_bill.id,
            category="other",
        )
        self.recalculate.execute(monthly_bill.id, self.user.id)

        created_ids = self.transpose.execute(str(file.id), self.user.id, card_id=self.card.id)

        self.assertNotEqual(created_ids[0], monthly_bill.id)
        shell = Transaction.objects.get(id=created_ids[0])

        result = self.apply_reconciliation.execute(
            {"bill_transaction_id": shell.id, "pairs": [], "categories": []},
            self.user.id,
        )

        self.assertEqual(result["merged_into_bill_id"], monthly_bill.id)
        shell.refresh_from_db()
        self.assertIsNotNone(shell.deleted_at)
        monthly_bill_instance = Transaction.objects.get(id=monthly_bill.id)
        self.assertEqual(monthly_bill_instance.file_id, file.id)
        self.assertEqual(monthly_bill_instance.total_amount, Decimal("40"))
        self.assertEqual(
            len(
                self.sub_transaction_repository.get_all_by_transaction_id(
                    monthly_bill.id, self.user.id
                )
            ),
            2,
        )
