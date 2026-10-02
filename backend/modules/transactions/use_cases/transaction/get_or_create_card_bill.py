import calendar
from datetime import date

from modules.cards.repositories.card import CardRepository
from modules.transactions.domains import TransactionDomain
from modules.transactions.factories import TransactionFactory
from modules.transactions.repositories import TransactionRepository
from modules.transactions.types import TransactionCategory


class GetOrCreateCardBillUseCase:
    """Resolves the single monthly bill for a card/competência month.

    The bill is the transaction that represents the card month: it may still be
    accumulating real-time launches (`file=None`) or already be an imported bill
    (`file_id` set). Never creates a second transaction for the same card/month.
    """

    def __init__(
        self,
        card_repository: CardRepository,
        transaction_repository: TransactionRepository,
        transaction_factory: TransactionFactory,
    ):
        self.card_repository = card_repository
        self.transaction_repository = transaction_repository
        self.transaction_factory = transaction_factory

    def execute(self, user_id: int, card_id: int, year: int, month: int) -> TransactionDomain:
        existing = self.transaction_repository.get_bill_by_card(user_id, card_id, year, month)
        if existing is not None:
            return existing

        card = self.card_repository.get(card_id, user_id)
        last_day = calendar.monthrange(year, month)[1]
        due_day = min(max(int(card.due_day or 1), 1), last_day)
        bill = self.transaction_factory.build(
            {
                "due_date": date(year, month, due_day).isoformat(),
                "total_amount": 0,
                "transaction_identifier": f"Fatura {card.name} {month:02d}/{year}",
                "transaction_type": "outgoing",
                "is_salary": False,
                "user_id": user_id,
                "is_recurrent": False,
                "category": TransactionCategory.CREDIT_CARD.name,
                "card_id": card.id,
            }
        )
        return self.transaction_repository.create(bill)
