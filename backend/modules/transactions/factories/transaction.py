from modules.transactions.domains import TransactionDomain
from modules.transactions.models import Transaction


class TransactionFactory:
    def build_from_model(self, model: Transaction) -> TransactionDomain:
        return TransactionDomain(
            due_date=model.due_date,
            total_amount=model.total_amount,
            transaction_identifier=model.transaction_identifier,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            transaction_type=model.transaction_type,
            is_salary=model.is_salary,
            user_id=model.user.id,
            is_recurrent=model.is_recurrent,
            installment_number=model.installment_number,
            main_transaction=model.main_transaction,
            recurrence_count=model.recurrence_count,
            amount_from_actor=model.get_total_from_actors(),
        )
    
    def build_from_serialized(self, serialized_transaction: dict) -> TransactionDomain:
        return TransactionDomain(
            due_date=serialized_transaction["due_date"],
            total_amount=serialized_transaction["total_amount"],
            transaction_identifier=serialized_transaction["transaction_identifier"],
            id=serialized_transaction["id"],
            created_at=serialized_transaction["created_at"],
            updated_at=serialized_transaction["updated_at"],
            transaction_type=serialized_transaction["transaction_type"],
            is_salary=serialized_transaction["is_salary"],
            is_recurrent=serialized_transaction["is_recurrent"],
            installment_number=serialized_transaction["installment_number"],
            main_transaction=serialized_transaction["main_transaction"],
            recurrence_count=serialized_transaction["recurrence_count"],
        )
    
    def build(self, data: dict) -> TransactionDomain:
        return TransactionDomain(
            due_date=data["due_date"],
            total_amount=data["total_amount"],
            transaction_identifier=data["transaction_identifier"],
            transaction_type=data["transaction_type"],
            is_salary=data.get("is_salary", False),
            user_id=data["user_id"],
            is_recurrent=data.get("is_recurrent", False),
            installment_number=data.get("installment_number", None),
            main_transaction=data.get("main_transaction", None),
            recurrence_count=data.get("recurrence_count", None),
        )
