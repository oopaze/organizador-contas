from datetime import datetime

from modules.transactions.factories import TransactionFactory
from modules.transactions.repositories import TransactionRepository
from modules.transactions.serializers import TransactionSerializer
from modules.transactions.types import TransactionCategory
from modules.transactions.use_cases.sub_transaction.create import CreateSubTransactionUseCase
from modules.transactions.use_cases.transaction.recalculate_amount import RecalculateAmountUseCase


class QuickAddTransactionUseCase:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        transaction_factory: TransactionFactory,
        transaction_serializer: TransactionSerializer,
        create_sub_transaction_use_case: CreateSubTransactionUseCase,
        recalculate_amount_use_case: RecalculateAmountUseCase,
    ):
        self.transaction_repository = transaction_repository
        self.transaction_factory = transaction_factory
        self.transaction_serializer = transaction_serializer
        self.create_sub_transaction_use_case = create_sub_transaction_use_case
        self.recalculate_amount_use_case = recalculate_amount_use_case

    def execute(self, data: dict, user_id: int) -> dict:
        if data.get("payment_method") == "credit":
            return self._execute_credit(data, user_id)
        return self._execute_cash(data, user_id)

    def _execute_cash(self, data: dict, user_id: int) -> dict:
        paid_at = data["date"] if data.get("is_paid", True) else None
        category = data.get("category") or TransactionCategory.OTHER.name
        transaction = self.transaction_factory.build(
            {
                "due_date": data["date"],
                "total_amount": data["amount"],
                "transaction_identifier": data["description"],
                "transaction_type": data.get("direction", "outgoing"),
                "is_salary": False,
                "user_id": user_id,
                "is_recurrent": False,
                "category": category,
                "paid_at": paid_at,
            }
        )
        created = self.transaction_repository.create(transaction)
        sub_transaction = self.create_sub_transaction_use_case.execute(
            self._sub_data(created.id, data, category, paid_at),
            user_id,
        )
        return {
            "transaction": self.transaction_serializer.serialize(created),
            "sub_transaction_id": sub_transaction["id"],
            "open_bill_total": None,
        }

    def _execute_credit(self, data: dict, user_id: int) -> dict:
        card_label = (data.get("card_label") or "").strip()
        if not card_label:
            raise ValueError("card_label é obrigatório para lançamento no cartão")

        purchase_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        identifier = f"Fatura {card_label} {purchase_date.month:02d}/{purchase_date.year}"
        open_bill = self.transaction_repository.get_open_bill(
            user_id, identifier, purchase_date.year, purchase_date.month
        )
        if open_bill is None:
            open_bill = self.transaction_factory.build(
                {
                    "due_date": purchase_date.replace(day=1).isoformat(),
                    "total_amount": 0,
                    "transaction_identifier": identifier,
                    "transaction_type": "outgoing",
                    "is_salary": False,
                    "user_id": user_id,
                    "is_recurrent": False,
                    "category": TransactionCategory.CREDIT_CARD.name,
                }
            )
            open_bill = self.transaction_repository.create(open_bill)

        category = data.get("category") or TransactionCategory.OTHER.name
        sub_transaction = self.create_sub_transaction_use_case.execute(
            self._sub_data(open_bill.id, data, category, paid_at=None),
            user_id,
        )
        self.recalculate_amount_use_case.execute(open_bill.id, user_id)
        updated_bill = self.transaction_repository.get(open_bill.id, user_id)

        return {
            "transaction": self.transaction_serializer.serialize(updated_bill),
            "sub_transaction_id": sub_transaction["id"],
            "open_bill_total": str(updated_bill.total_amount),
        }

    def _sub_data(self, transaction_id: int, data: dict, category: str, paid_at) -> dict:
        sub_data = {
            "transaction_id": transaction_id,
            "description": data["description"],
            "amount": data["amount"],
            "date": data["date"],
            "category": category,
            "paid_at": paid_at,
        }
        if data.get("actor_id"):
            sub_data["actor"] = data["actor_id"]
        return sub_data
