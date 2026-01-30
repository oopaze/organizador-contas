from modules.transactions.domains import TransactionDomain
from modules.transactions.factories.transaction import TransactionFactory
from modules.transactions.models import Transaction


class TransactionRepository:
    def __init__(self, model: Transaction, transaction_factory: TransactionFactory):
        self.model = model
        self.transaction_factory = transaction_factory
        self.queryset = self.model.objects.order_by("id")

    def filter(self, filters: dict) -> list["TransactionDomain"]:
        queryset = self.queryset.filter(**filters)
        return [self.transaction_factory.build_from_model(transaction) for transaction in queryset]

    def get(self, transaction_id: str, user_id: int) -> "TransactionDomain":
        transaction_instance = self.queryset.get(id=transaction_id, user_id=user_id)
        return self.transaction_factory.build_from_model(transaction_instance)
    
    def get_all(self, user_id: int) -> list["TransactionDomain"]:
        transaction_instances = self.queryset.filter(user_id=user_id)
        return [self.transaction_factory.build_from_model(transaction) for transaction in transaction_instances]
    
    def create(self, transaction: "TransactionDomain") -> "TransactionDomain":
        transaction_instance = self.model.objects.create(
            due_date=transaction.due_date,
            total_amount=transaction.total_amount,
            transaction_identifier=transaction.transaction_identifier,
            transaction_type=transaction.transaction_type,
            is_salary=transaction.is_salary,
            user_id=transaction.user_id,
            is_recurrent=transaction.is_recurrent,
            installment_number=transaction.installment_number,
            main_transaction_id=transaction.main_transaction,
            recurrence_count=transaction.recurrence_count,
        )
        return self.transaction_factory.build_from_model(transaction_instance)
    
    def update(self, transaction: "TransactionDomain") -> "TransactionDomain":
        transaction_instance = self.queryset.get(id=transaction.id, user_id=transaction.user_id)
        transaction_instance.due_date = transaction.due_date
        transaction_instance.total_amount = transaction.total_amount
        transaction_instance.transaction_identifier = transaction.transaction_identifier
        transaction_instance.transaction_type = transaction.transaction_type
        transaction_instance.is_salary = transaction.is_salary
        transaction_instance.is_recurrent = transaction.is_recurrent
        transaction_instance.save()
        return self.transaction_factory.build_from_model(transaction_instance)
    
    def delete(self, transaction_id: str, user_id: int):
        self.queryset.get(id=transaction_id, user_id=user_id).delete()

