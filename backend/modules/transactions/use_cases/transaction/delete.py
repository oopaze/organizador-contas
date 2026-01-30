from modules.transactions.repositories import TransactionRepository


class DeleteTransactionUseCase:
    def __init__(self, transaction_repository: TransactionRepository):
        self.transaction_repository = transaction_repository

    def execute(self, transaction_id: str, user_id: int):
        transaction = self.transaction_repository.get(transaction_id, user_id)
        if transaction.is_recurrent:
            children_transactions = self.transaction_repository.get_children_transactions(transaction_id, user_id)
            self.transaction_repository.delete_many(children_transactions)
        self.transaction_repository.delete(transaction_id, user_id)
