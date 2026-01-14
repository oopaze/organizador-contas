from typing import TYPE_CHECKING

from modules.transactions.domains import SubTransactionDomain
from modules.transactions.models import SubTransaction

if TYPE_CHECKING:
    from modules.transactions.factories import SubTransactionFactory


class SubTransactionRepository:
    def __init__(self, model: SubTransaction, sub_transaction_factory: "SubTransactionFactory"):
        self.model = model
        self.sub_transaction_factory = sub_transaction_factory

    def get(self, sub_transaction_id: str) -> "SubTransactionDomain":
        sub_transaction_instance = self.model.objects.get(id=sub_transaction_id)
        return self.sub_transaction_factory.build_from_model(sub_transaction_instance)

    def get_all(self) -> list["SubTransactionDomain"]:
        sub_transaction_instances = self.model.objects.all()
        return [
            self.sub_transaction_factory.build_from_model(sub_transaction_instance)
            for sub_transaction_instance in sub_transaction_instances
        ]
    
    def create(self, sub_transaction: "SubTransactionDomain") -> "SubTransactionDomain":
        if sub_transaction.actor:
            actor_id = sub_transaction.actor.id
        else:
            actor_id = None

        sub_transaction_instance = self.model.objects.create(
            date=sub_transaction.date,
            description=sub_transaction.description,
            amount=sub_transaction.amount,
            installment_info=sub_transaction.installment_info,
            transaction_id=sub_transaction.transaction.id,
            actor_id=actor_id,
        )
        return self.sub_transaction_factory.build_from_model(sub_transaction_instance)
    
    def create_many(self, sub_transactions: list["SubTransactionDomain"]) -> list["SubTransactionDomain"]:
        return [
            self.create(sub_transaction) for sub_transaction in sub_transactions
        ]
    
    def update(self, sub_transaction: "SubTransactionDomain") -> "SubTransactionDomain":
        sub_transaction_instance = self.model.objects.get(id=sub_transaction.id)
        sub_transaction_instance.date = sub_transaction.date
        sub_transaction_instance.description = sub_transaction.description
        sub_transaction_instance.amount = sub_transaction.amount
        sub_transaction_instance.installment_info = sub_transaction.installment_info
        sub_transaction_instance.transaction_id = sub_transaction.transaction.id
        if sub_transaction.actor:
            sub_transaction_instance.actor_id = sub_transaction.actor.id
        sub_transaction_instance.save()
        return self.sub_transaction_factory.build_from_model(sub_transaction_instance)
    
    def delete(self, sub_transaction_id: str):
        self.model.objects.get(id=sub_transaction_id).delete()
