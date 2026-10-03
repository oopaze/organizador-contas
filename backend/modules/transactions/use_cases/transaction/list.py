from typing import TypedDict

from modules.transactions.repositories import SubTransactionRepository, TransactionRepository
from modules.transactions.serializers import TransactionSerializer


class ListTransactionsFilters(TypedDict, total=False):
    transaction_type: str
    due_date: str


class ListTransactionsUseCase:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        transaction_serializer: TransactionSerializer,
        sub_transaction_repository: SubTransactionRepository,
    ):
        self.transaction_repository = transaction_repository
        self.transaction_serializer = transaction_serializer
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, filters: ListTransactionsFilters = {}, include_subtransactions: bool = False) -> list[dict]:
        transactions = self.transaction_repository.filter(filters=filters)
        if include_subtransactions and transactions:
            sub_transactions = self.sub_transaction_repository.get_all_by_transaction_ids(
                [transaction.id for transaction in transactions]
            )
            grouped: dict[int, list] = {}
            for sub_transaction in sub_transactions:
                grouped.setdefault(sub_transaction.transaction.id, []).append(sub_transaction)
            for transaction in transactions:
                transaction.set_sub_transactions(grouped.get(transaction.id, []))
        return [self.transaction_serializer.serialize(transaction) for transaction in transactions]
