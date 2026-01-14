from modules.transactions.repositories import SubTransactionRepository
from modules.transactions.serializers import SubTransactionSerializer


class ListSubTransactionsUseCase:
    def __init__(self, sub_transaction_repository: SubTransactionRepository, sub_transaction_serializer: SubTransactionSerializer):
        self.sub_transaction_repository = sub_transaction_repository
        self.sub_transaction_serializer = sub_transaction_serializer

    def execute(self) -> list[dict]:
        sub_transactions = self.sub_transaction_repository.get_all()
        return [self.sub_transaction_serializer.serialize(sub_transaction) for sub_transaction in sub_transactions]
