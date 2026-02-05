from django.utils import timezone

from modules.transactions.repositories import SubTransactionRepository


class PaySubTransactionUseCase:
    def __init__(self, sub_transaction_repository: SubTransactionRepository):
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, sub_transaction_id: int, user_id: int):
        sub_transaction = self.sub_transaction_repository.get(sub_transaction_id, user_id)
        is_paying = sub_transaction.is_paying()
        
        if is_paying:
            sub_transaction.pay()
        else:
            sub_transaction.unpay()
        
        self.sub_transaction_repository.update_paid_at(sub_transaction)

        return {"message": "success"}
