from modules.transactions.repositories import TransactionRepository
from modules.transactions.serializers import TransactionSerializer


class UpdateTransactionUseCase:
    def __init__(self, transaction_repository: TransactionRepository, transaction_serializer: TransactionSerializer):
        self.transaction_repository = transaction_repository
        self.transaction_serializer = transaction_serializer

    def execute(self, id: int, data: dict) -> dict:
        transaction = self.transaction_repository.get(id, data["user_id"])
        transaction.update(data)
        updated_transaction = self.transaction_repository.update(transaction)
        return self.transaction_serializer.serialize(updated_transaction)
