from modules.transactions.repositories import SubTransactionRepository
from modules.transactions.serializers import SubTransactionSerializer


class ListSubTransactionsUseCase:
    def __init__(self, sub_transaction_repository: SubTransactionRepository, sub_transaction_serializer: SubTransactionSerializer):
        self.sub_transaction_repository = sub_transaction_repository
        self.sub_transaction_serializer = sub_transaction_serializer

    def execute(self, user_id: int, due_date: str = None, actor_id: str = None) -> list[dict]:
        sub_transactions = self.sub_transaction_repository.get_all(user_id, due_date, actor_id)
        return [self.sub_transaction_serializer.serialize(sub_transaction) for sub_transaction in sub_transactions]
