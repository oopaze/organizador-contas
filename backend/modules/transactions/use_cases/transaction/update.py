from datetime import datetime
from dateutil.relativedelta import relativedelta

from modules.transactions.repositories import TransactionRepository
from modules.transactions.serializers import TransactionSerializer
from modules.transactions.repositories import SubTransactionRepository

if TYPE_CHECKING:
    from modules.transactions.domains import TransactionDomain, SubTransactionDomain


class UpdateTransactionUseCase:
    def __init__(self, transaction_repository: TransactionRepository, transaction_serializer: TransactionSerializer, sub_transaction_repository: SubTransactionRepository):
        self.transaction_repository = transaction_repository
        self.transaction_serializer = transaction_serializer
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, id: int, data: dict) -> dict:
        transaction = self.transaction_repository.get(id, data["user_id"])
        transaction.update(data)

        if transaction.is_recurrent:
            children_transactions = self.transaction_repository.get_children_transactions(transaction.id, data["user_id"])
            if len(children_transactions):
                self.update_children_transactions(transaction, data)

        self.update_single_sub_transaction(transaction)

        updated_transaction = self.transaction_repository.update(transaction)
        return self.transaction_serializer.serialize(updated_transaction)
    
    def update_single_sub_transaction(self, transaction: "TransactionDomain") -> "SubTransactionDomain":
        sub_transactions = self.sub_transaction_repository.get_all_by_transaction_id(transaction.id, transaction.user_id)
        if len(sub_transactions) == 1:
            sub_transaction = sub_transactions[0]
            sub_transaction.update({
                "description": transaction.transaction_identifier,
                "amount": transaction.total_amount,
            })
            self.sub_transaction_repository.update(sub_transaction)
    
    def update_children_transactions(self, transaction: "TransactionDomain", data: dict) -> list["TransactionDomain"]:
        children_transactions = self.transaction_repository.get_children_transactions(transaction.id, transaction.user_id)
        if len(children_transactions) == 0:
            return []

        last_due_date = transaction.due_date
        for i, child_transaction in enumerate(children_transactions):
            data["due_date"] = self.calculate_next_due_date(last_due_date, i)
            child_transaction.update(data)
            self.update_single_sub_transaction(child_transaction)
        return self.transaction_repository.update_many(children_transactions)
    
    def calculate_next_due_date(self, due_date: str, recurrence_count: int) -> str:
        date_obj = datetime.strptime(due_date, "%Y-%m-%d")
        next_date = date_obj + relativedelta(months=recurrence_count)
        return next_date.strftime("%Y-%m-%d")
