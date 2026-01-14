from modules.transactions.repositories import SubTransactionRepository
from modules.transactions.serializers import SubTransactionSerializer


class UpdateSubTransactionUseCase:
    def __init__(self, sub_transaction_repository: SubTransactionRepository, sub_transaction_serializer: SubTransactionSerializer):
        self.sub_transaction_repository = sub_transaction_repository
        self.sub_transaction_serializer = sub_transaction_serializer

    def execute(self, id: int, data: dict) -> dict:
        sub_transaction = self.sub_transaction_repository.get(id)
        sub_transaction.update(data)
        updated_sub_transaction = self.sub_transaction_repository.update(sub_transaction)
        return self.sub_transaction_serializer.serialize(updated_sub_transaction)
