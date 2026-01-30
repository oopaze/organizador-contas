from datetime import datetime, timedelta

from modules.transactions.factories import TransactionFactory, SubTransactionFactory
from modules.transactions.repositories import TransactionRepository, SubTransactionRepository
from modules.transactions.serializers import TransactionSerializer
from modules.transactions.domains import TransactionDomain, SubTransactionDomain


class CreateTransactionUseCase:
    def __init__(
        self, 
        transaction_repository: TransactionRepository, 
        transaction_serializer: TransactionSerializer, 
        transaction_factory: TransactionFactory,
        sub_transaction_factory: SubTransactionFactory,
        sub_transaction_repository: SubTransactionRepository,
    ):
        self.transaction_repository = transaction_repository
        self.transaction_serializer = transaction_serializer
        self.transaction_factory = transaction_factory
        self.sub_transaction_factory = sub_transaction_factory
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, data: dict) -> dict:
        if data.get("is_recurrent", False):
            return self.execute_if_recurrent(data)
        return self.execute_if_not_recurrent(data)
    
    def execute_if_not_recurrent(self, data: dict) -> dict:
        transaction = self.transaction_factory.build(data)
        created_transaction = self.transaction_repository.create(transaction)
        if not created_transaction.is_salary:
            self.create_sub_transaction(created_transaction)
        return self.transaction_serializer.serialize(created_transaction)
    
    def execute_if_recurrent(self, data: dict) -> dict:
        recurrence_count = data.get("recurrence_count")
        first_created_transaction = None
        for i in range(recurrence_count):
            data["installment_number"] = i + 1
            if i > 0:
                data["main_transaction"] = first_created_transaction.id
                
            transaction = self.transaction_factory.build(data)
            created_transaction = self.transaction_repository.create(transaction)
            self.create_sub_transaction(created_transaction, installment=f"{i+1}/{recurrence_count}")
            data["due_date"] = self.calculate_next_due_date(data["due_date"])
            if i == 0:
                first_created_transaction = created_transaction
        return self.transaction_serializer.serialize(first_created_transaction)
    
    def create_sub_transaction(self, transaction: "TransactionDomain", installment: str = "1/1") -> "SubTransactionDomain":
        sub_transaction = self.sub_transaction_factory.build_from_transaction(transaction, installment)
        return self.sub_transaction_repository.create(sub_transaction)

    def calculate_next_due_date(self, due_date: str) -> str:
        date = datetime.strptime(due_date, "%Y-%m-%d")
        days_to_add = 28 if date.month == 1 and date.day > 30 else 30
        next_date = date + timedelta(days=days_to_add)
        return next_date.strftime("%Y-%m-%d")
