from modules.transactions.repositories import SubTransactionRepository


class DeleteSubTransactionUseCase:
    def __init__(self, sub_transaction_repository: SubTransactionRepository):
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, sub_transaction_id: str, user_id: int):
        sub_transaction = self.sub_transaction_repository.get(sub_transaction_id, user_id)
        self.sub_transaction_repository.delete(sub_transaction.id)
