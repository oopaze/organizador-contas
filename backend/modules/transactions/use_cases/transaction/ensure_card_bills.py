import calendar
from datetime import date

from django.db import transaction

from modules.cards.repositories.card import CardRepository
from modules.transactions.factories import TransactionFactory
from modules.transactions.repositories import TransactionRepository
from modules.transactions.serializers import TransactionSerializer
from modules.transactions.types import TransactionCategory
from modules.transactions.use_cases.transaction.recalculate_amount import RecalculateAmountUseCase


class EnsureMonthlyCardBillsUseCase:
    """Guarantees one open bill per active card/month, even when zeroed.

    The bill is anchored on the competência month using the card due day
    (clamped to the month end) so the app's monthly filter keeps working.
    Idempotent: one bill per card/month.
    """

    def __init__(
        self,
        card_repository: CardRepository,
        transaction_repository: TransactionRepository,
        transaction_factory: TransactionFactory,
        transaction_serializer: TransactionSerializer,
        recalculate_amount_use_case: RecalculateAmountUseCase,
    ):
        self.card_repository = card_repository
        self.transaction_repository = transaction_repository
        self.transaction_factory = transaction_factory
        self.transaction_serializer = transaction_serializer
        self.recalculate_amount_use_case = recalculate_amount_use_case

    def execute(self, user_id: int, month: str) -> dict:
        year, month_number = self._parse_month(month)
        last_day = calendar.monthrange(year, month_number)[1]
        bills = []

        for card in self.card_repository.get_all(user_id, only_active=True):
            due_day = min(max(int(card.due_day or 1), 1), last_day)
            due_date = date(year, month_number, due_day).isoformat()
            identifier = f"Fatura {card.name} {month_number:02d}/{year}"

            with transaction.atomic():
                locked_card = self.card_repository.get_for_update(card.id, user_id)
                bill = self.transaction_repository.get_open_bill_by_card(
                    user_id, locked_card.id, year, month_number
                )
                created_now = False
                if bill is None:
                    if self.transaction_repository.exists_including_deleted(
                        user_id=user_id,
                        card_id=locked_card.id,
                        category=TransactionCategory.CREDIT_CARD.name,
                        due_date__year=year,
                        due_date__month=month_number,
                    ):
                        continue
                    legacy = self.transaction_repository.get_open_bill(
                        user_id, identifier, year, month_number
                    )
                    if legacy is not None and legacy.card_id is None:
                        legacy.card_id = locked_card.id
                        bill = self.transaction_repository.update(legacy)
                    else:
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
                                "card_id": locked_card.id,
                            }
                        )
                        bill = self.transaction_repository.create(bill)
                        created_now = True

                if not created_now and str(bill.due_date) != due_date:
                    bill.due_date = due_date
                    bill = self.transaction_repository.update(bill)

            self.recalculate_amount_use_case.execute(bill.id, user_id)
            updated = self.transaction_repository.get(bill.id, user_id)
            bills.append(self.transaction_serializer.serialize(updated))

        return {"bills": bills}

    def _parse_month(self, month: str) -> tuple[int, int]:
        try:
            year, month_number = str(month).split("-")
            year, month_number = int(year), int(month_number)
        except (TypeError, ValueError):
            raise ValueError("month deve estar no formato YYYY-MM")
        if month_number < 1 or month_number > 12:
            raise ValueError("month deve estar no formato YYYY-MM")
        return year, month_number
