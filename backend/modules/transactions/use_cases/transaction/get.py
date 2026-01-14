from modules.transactions.repositories import TransactionRepository, SubTransactionRepository
from modules.transactions.serializers import TransactionSerializer


class GetTransactionUseCase:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        transaction_serializer: TransactionSerializer,
        sub_transaction_repository: SubTransactionRepository,
    ):
        self.transaction_repository = transaction_repository
        self.transaction_serializer = transaction_serializer
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, transaction_id: str, user_id: int) -> dict:
        transaction = self.transaction_repository.get(transaction_id, user_id)
        sub_transactions = self.sub_transaction_repository.get_all_by_transaction_id(transaction_id)
        transaction.set_sub_transactions(sub_transactions)
        return self.transaction_serializer.serialize(transaction)
