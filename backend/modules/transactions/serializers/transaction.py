from modules.transactions.domains import TransactionDomain
from modules.transactions.types import TransactionCategory
from modules.transactions.serializers.sub_transaction import SubTransactionSerializer


TRANSACTION_FOR_TOOL_PROMPT = """
Transaction {transaction_identifier}:
- id: {transaction_id}
- Due Date: {due_date}
- Total Amount: {total_amount}
- Transaction Type: {transaction_type}
- Recurrence Count: {recurrence_count}
- Installment Number: {installment_number}
- Main Transaction: {main_transaction}
- Is Credit Card: {is_credit_card}
- Category: {category}
"""


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
            "amount_from_actor": transaction.amount_from_actor if transaction.amount_from_actor else None,
            "paid_at": transaction.paid_at.strftime("%Y-%m-%d %H:%M:%S") if transaction.paid_at else None,
            "subtransactions_paid": transaction.subtransactions_paid,
            "is_paid": transaction.is_paid,
            "category": TransactionCategory.get_by_name(transaction.category).value,
        }
    
    def serialize_for_tool(self, transaction: "TransactionDomain") -> str:
        return TRANSACTION_FOR_TOOL_PROMPT.format(
            transaction_identifier=transaction.transaction_identifier,
            transaction_id=transaction.id,
            due_date=transaction.due_date,
            total_amount=transaction.total_amount,
            transaction_type=transaction.transaction_type,
            recurrence_count=transaction.recurrence_count,
            installment_number=transaction.installment_number,
            main_transaction=transaction.main_transaction.id if transaction.main_transaction else None,
            is_credit_card=transaction.file_id is not None,
            category=transaction.category,
        )
    
    def serialize_many_for_tool(self, transactions: list["TransactionDomain"]) -> str:
        return "\n".join([self.serialize_for_tool(transaction) for transaction in transactions])
