from modules.transactions.repositories import TransactionRepository, SubTransactionRepository


class RecalculateAmountUseCase:
    def __init__(self, transaction_repository: TransactionRepository, sub_transaction_repository: SubTransactionRepository):
        self.transaction_repository = transaction_repository
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, transaction_id: int, user_id: int):
        transaction = self.transaction_repository.get(transaction_id, user_id)
        sub_transactions = self.sub_transaction_repository.get_all_by_transaction_id(transaction_id, user_id)
        total_amount = sum([sub_transaction.amount for sub_transaction in sub_transactions])
        transaction.update_amount(total_amount)
        self.transaction_repository.update(transaction)
        return {"message": "success"}
