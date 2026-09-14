import calendar
from datetime import datetime
from decimal import ROUND_DOWN, Decimal

from dateutil.relativedelta import relativedelta
from django.db import transaction

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
        infer_category_use_case=None,
        card_repository=None,
    ):
        self.transaction_repository = transaction_repository
        self.transaction_factory = transaction_factory
        self.transaction_serializer = transaction_serializer
        self.create_sub_transaction_use_case = create_sub_transaction_use_case
        self.recalculate_amount_use_case = recalculate_amount_use_case
        self.infer_category_use_case = infer_category_use_case
        self.card_repository = card_repository

    def _resolve_category(self, data: dict, user_id: int) -> str:
        category = data.get("category")
        if category:
            return category
        if self.infer_category_use_case is not None:
            try:
                return self.infer_category_use_case.execute(data["description"], user_id)
            except Exception:
                return TransactionCategory.OTHER.name
        return TransactionCategory.OTHER.name

    def _resolve_card(self, data: dict, user_id: int):
        if self.card_repository is None:
            return None
        if data.get("card_id"):
            return self.card_repository.get_or_none(data["card_id"], user_id)
        card_label = (data.get("card_label") or "").strip()
        if card_label:
            return self.card_repository.get_by_name(user_id, card_label)
        return None

    def execute(self, data: dict, user_id: int) -> dict:
        installments = self._installments(data)
        if data.get("payment_method") == "credit":
            return self._execute_credit(data, user_id, installments)
        return self._execute_cash(data, user_id, installments)

    def _installments(self, data: dict) -> int:
        try:
            installments = int(data.get("installments", 1))
        except (TypeError, ValueError):
            raise ValueError("installments deve ser um número inteiro")
        if installments < 1:
            raise ValueError("installments deve ser maior ou igual a 1")
        return installments

    def _amounts(self, amount, installments: int) -> list[Decimal]:
        total = Decimal(str(amount))
        base = (total / installments).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        amounts = [base] * (installments - 1)
        amounts.append(total - base * (installments - 1))
        return amounts

    def _add_months(self, date: str, months: int) -> str:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        return (date_obj + relativedelta(months=months)).isoformat()

    def _execute_cash(self, data: dict, user_id: int, installments: int = 1) -> dict:
        if installments > 1:
            return self._execute_cash_installments(data, user_id, installments)

        paid_at = data["date"] if data.get("is_paid", True) else None
        category = self._resolve_category(data, user_id)
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

    def _execute_cash_installments(self, data: dict, user_id: int, installments: int) -> dict:
        paid_at = data["date"] if data.get("is_paid", True) else None
        category = self._resolve_category(data, user_id)
        amounts = self._amounts(data["amount"], installments)
        first_transaction = None
        first_sub_transaction_id = None

        for index, amount in enumerate(amounts):
            due_date = self._add_months(data["date"], index)
            installment_paid_at = paid_at if index == 0 else None
            transaction = self.transaction_factory.build(
                {
                    "due_date": due_date,
                    "total_amount": amount,
                    "transaction_identifier": data["description"],
                    "transaction_type": data.get("direction", "outgoing"),
                    "is_salary": False,
                    "user_id": user_id,
                    "is_recurrent": False,
                    "installment_number": index + 1,
                    "recurrence_count": installments,
                    "main_transaction": first_transaction.id if first_transaction else None,
                    "category": category,
                    "paid_at": installment_paid_at,
                }
            )
            created = self.transaction_repository.create(transaction)
            sub_transaction = self.create_sub_transaction_use_case.execute(
                self._sub_data(
                    created.id,
                    {**data, "date": due_date, "amount": amount},
                    category,
                    installment_paid_at,
                    installment_info=f"{index + 1}/{installments}",
                ),
                user_id,
            )
            if index == 0:
                first_transaction = created
                first_sub_transaction_id = sub_transaction["id"]

        return {
            "transaction": self.transaction_serializer.serialize(first_transaction),
            "sub_transaction_id": first_sub_transaction_id,
            "open_bill_total": None,
        }

    def _get_or_create_bill(self, user_id: int, card, identifier: str, year: int, month: int, due_date: str):
        if card is None:
            bill = self.transaction_repository.get_open_bill(user_id, identifier, year, month)
            if bill is None:
                bill = self._create_bill(user_id, None, identifier, due_date)
            return bill

        with transaction.atomic():
            locked_card = self.card_repository.get_for_update(card.id, user_id)
            bill = self.transaction_repository.get_open_bill_by_card(
                user_id, locked_card.id, year, month
            )
            if bill is None:
                legacy = self.transaction_repository.get_open_bill(
                    user_id, identifier, year, month
                )
                if legacy is not None:
                    legacy.card_id = locked_card.id
                    return self.transaction_repository.update(legacy)
                bill = self._create_bill(user_id, locked_card.id, identifier, due_date)
            return bill

    def _create_bill(self, user_id: int, card_id, identifier: str, due_date: str):
        bill = self.transaction_factory.build(
            {
                "due_date": due_date,
                "total_amount": 0,
                "transaction_identifier": identifier,
                "transaction_type": "outgoing",
                "is_salary": False,
                "user_id": user_id,
                "is_recurrent": False,
                "category": TransactionCategory.CREDIT_CARD.name,
                "card_id": card_id,
            }
        )
        return self.transaction_repository.create(bill)

    def _bill_due_date(self, anchor, card) -> str:
        if card is None:
            return anchor.replace(day=1).isoformat()
        last_day = calendar.monthrange(anchor.year, anchor.month)[1]
        due_day = min(max(int(card.due_day or 1), 1), last_day)
        return anchor.replace(day=due_day).isoformat()

    def _execute_credit(self, data: dict, user_id: int, installments: int = 1) -> dict:
        if installments > 1:
            return self._execute_credit_installments(data, user_id, installments)

        card = self._resolve_card(data, user_id)
        card_label = card.name if card else (data.get("card_label") or "").strip()
        if not card_label:
            raise ValueError("card_label é obrigatório para lançamento no cartão")

        purchase_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        identifier = f"Fatura {card_label} {purchase_date.month:02d}/{purchase_date.year}"
        open_bill = self._get_or_create_bill(
            user_id,
            card,
            identifier,
            purchase_date.year,
            purchase_date.month,
            self._bill_due_date(purchase_date, card),
        )

        category = self._resolve_category(data, user_id)
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

    def _execute_credit_installments(self, data: dict, user_id: int, installments: int) -> dict:
        card = self._resolve_card(data, user_id)
        card_label = card.name if card else (data.get("card_label") or "").strip()
        if not card_label:
            raise ValueError("card_label é obrigatório para lançamento no cartão")

        purchase_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        category = self._resolve_category(data, user_id)
        amounts = self._amounts(data["amount"], installments)
        first_bill = None
        first_sub_transaction_id = None

        for index, amount in enumerate(amounts):
            installment_date = purchase_date + relativedelta(months=index)
            identifier = f"Fatura {card_label} {installment_date.month:02d}/{installment_date.year}"
            open_bill = self._get_or_create_bill(
                user_id,
                card,
                identifier,
                installment_date.year,
                installment_date.month,
                self._bill_due_date(installment_date, card),
            )

            sub_transaction = self.create_sub_transaction_use_case.execute(
                self._sub_data(
                    open_bill.id,
                    {**data, "date": installment_date.isoformat(), "amount": amount},
                    category,
                    paid_at=None,
                    installment_info=f"{index + 1}/{installments}",
                ),
                user_id,
            )
            self.recalculate_amount_use_case.execute(open_bill.id, user_id)

            if index == 0:
                first_bill = self.transaction_repository.get(open_bill.id, user_id)
                first_sub_transaction_id = sub_transaction["id"]

        return {
            "transaction": self.transaction_serializer.serialize(first_bill),
            "sub_transaction_id": first_sub_transaction_id,
            "open_bill_total": str(first_bill.total_amount),
        }

    def _sub_data(self, transaction_id: int, data: dict, category: str, paid_at, installment_info: str = None) -> dict:
        sub_data = {
            "transaction_id": transaction_id,
            "description": data["description"],
            "amount": data["amount"],
            "date": data["date"],
            "category": category,
            "paid_at": paid_at,
        }
        if installment_info:
            sub_data["installment_info"] = installment_info
        if data.get("actor_id"):
            sub_data["actor"] = data["actor_id"]
        return sub_data
