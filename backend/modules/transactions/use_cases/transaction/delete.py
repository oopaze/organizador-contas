from modules.transactions.repositories import TransactionRepository, SubTransactionRepository


class DeleteTransactionUseCase:
    def __init__(self, transaction_repository: TransactionRepository, sub_transaction_repository: SubTransactionRepository):
        self.transaction_repository = transaction_repository
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, transaction_id: str, user_id: int):
        transaction = self.transaction_repository.get(transaction_id, user_id)
        if transaction.is_recurrent:
            children_transactions = self.transaction_repository.get_children_transactions(transaction_id, user_id)
            for child_transaction in children_transactions:
                self._delete_transaction(child_transaction.id, user_id)
        self._delete_transaction(transaction_id, user_id)

    def _delete_transaction(self, transaction_id: str, user_id: int):
        self.transaction_repository.delete(transaction_id, user_id)
        sub_transactions = self.sub_transaction_repository.get_all_by_transaction_id(transaction_id, user_id)
        self.sub_transaction_repository.delete_many(sub_transactions)
        
