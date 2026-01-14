from typing import TypedDict

from modules.transactions.repositories import TransactionRepository
from modules.transactions.serializers import TransactionSerializer


class ListTransactionsFilters(TypedDict, total=False):
    transaction_type: str
    due_date: str


class ListTransactionsUseCase:
    def __init__(self, transaction_repository: TransactionRepository, transaction_serializer: TransactionSerializer):
        self.transaction_repository = transaction_repository
        self.transaction_serializer = transaction_serializer

    def execute(self, filters: ListTransactionsFilters = {}) -> list[dict]:
        transactions = self.transaction_repository.filter(filters=filters)
        return [self.transaction_serializer.serialize(transaction) for transaction in transactions]
