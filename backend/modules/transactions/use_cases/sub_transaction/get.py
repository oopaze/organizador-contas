from modules.transactions.repositories import SubTransactionRepository
from modules.transactions.serializers import SubTransactionSerializer


class GetSubTransactionUseCase:
    def __init__(self, sub_transaction_repository: SubTransactionRepository, sub_transaction_serializer: SubTransactionSerializer):
        self.sub_transaction_repository = sub_transaction_repository
        self.sub_transaction_serializer = sub_transaction_serializer

    def execute(self, sub_transaction_id: str, user_id: int) -> dict:
        sub_transaction = self.sub_transaction_repository.get(sub_transaction_id, user_id)
        return self.sub_transaction_serializer.serialize(sub_transaction)
