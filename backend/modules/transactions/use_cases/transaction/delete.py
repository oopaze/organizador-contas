from modules.transactions.repositories import TransactionRepository


class DeleteTransactionUseCase:
    def __init__(self, transaction_repository: TransactionRepository):
        self.transaction_repository = transaction_repository

    def execute(self, transaction_id: str, user_id: int):
        self.transaction_repository.delete(transaction_id, user_id)
