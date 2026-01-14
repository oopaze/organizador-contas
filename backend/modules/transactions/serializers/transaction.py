from modules.transactions.domains import TransactionDomain
from modules.transactions.serializers.sub_transaction import SubTransactionSerializer


class TransactionSerializer:
    def __init__(self, sub_transaction_serializer: SubTransactionSerializer):
        self.sub_transaction_serializer = sub_transaction_serializer

    def serialize(self, transaction: "TransactionDomain") -> dict:
        return {
            "id": transaction.id,
            "due_date": transaction.due_date,
            "total_amount": transaction.total_amount,
            "transaction_identifier": transaction.transaction_identifier,
            "transaction_type": transaction.transaction_type,
            "is_salary": transaction.is_salary,
            "created_at": transaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": transaction.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "sub_transactions": [self.sub_transaction_serializer.serialize(sub_transaction) for sub_transaction in transaction.sub_transactions],
            "is_recurrent": transaction.is_recurrent,
            "recurrence_count": transaction.recurrence_count,
            "installment_number": transaction.installment_number,
            "main_transaction": transaction.main_transaction.id if transaction.main_transaction else None,
        }
