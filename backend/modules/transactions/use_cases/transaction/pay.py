from modules.transactions.repositories import TransactionRepository, SubTransactionRepository


class PayTransactionUseCase:
    def __init__(self, transaction_repository: TransactionRepository, sub_transaction_repository: SubTransactionRepository):
        self.transaction_repository = transaction_repository
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, transaction_id: int, user_id: int, update_sub_transactions: bool = False):
        transaction = self.transaction_repository.get(transaction_id, user_id)
        is_paying = transaction.is_paying()
        if is_paying:
            transaction.pay()
        else:
            transaction.unpay()

        self.transaction_repository.update_paid_at(transaction)

        if update_sub_transactions:
            sub_transactions = self.sub_transaction_repository.get_all_by_transaction_id(transaction_id, user_id)
            for sub_transaction in sub_transactions:
                if is_paying:
                    sub_transaction.pay()
                else:
                    sub_transaction.unpay()
                self.sub_transaction_repository.update_paid_at(sub_transaction)

        return {"message": "success"}
