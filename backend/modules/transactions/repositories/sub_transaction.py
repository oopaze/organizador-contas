from typing import TYPE_CHECKING
from datetime import datetime
from django.utils import timezone

from modules.transactions.domains import SubTransactionDomain
from modules.transactions.models import SubTransaction

if TYPE_CHECKING:
    from modules.transactions.factories import SubTransactionFactory


class SubTransactionRepository:
    def __init__(self, model: SubTransaction, sub_transaction_factory: "SubTransactionFactory"):
        self.model = model
        self.sub_transaction_factory = sub_transaction_factory

    @property
    def queryset(self):
        return (
            self.model.objects
                .order_by("id")
                .select_related("actor")
                .select_related("transaction")
                .exclude(deleted_at__isnull=False)
        )

    def get(self, sub_transaction_id: str, user_id: int) -> "SubTransactionDomain":
        sub_transaction_instance = self.queryset.get(id=sub_transaction_id, transaction__user_id=user_id)
        return self.sub_transaction_factory.build_from_model(sub_transaction_instance)
    
    def get_by_actor_id(self, actor_id: str, user_id: int, due_date: str = None) -> "SubTransactionDomain":
        sub_transaction_instances = self.queryset.filter(actor_id=actor_id, transaction__user_id=user_id)

        if due_date:
            date = datetime.strptime(due_date, "%Y-%m-%d")
            sub_transaction_instances = sub_transaction_instances.filter(
                transaction__due_date__month=date.month, 
                transaction__due_date__year=date.year
            )

        return [
            self.sub_transaction_factory.build_from_model(sub_transaction_instance)
            for sub_transaction_instance in sub_transaction_instances
        ]

    def get_all(self, user_id: int, due_date: str = None, actor_id: str = None) -> list["SubTransactionDomain"]:
        sub_transaction_instances = self.queryset.filter(transaction__user_id=user_id)

        if due_date:
            date = datetime.strptime(due_date, "%Y-%m-%d")
            sub_transaction_instances = sub_transaction_instances.filter(
                transaction__due_date__month=date.month, 
                transaction__due_date__year=date.year
            )

        if actor_id:
            sub_transaction_instances = sub_transaction_instances.filter(actor_id=actor_id)

        return [
            self.sub_transaction_factory.build_from_model(sub_transaction_instance)
            for sub_transaction_instance in sub_transaction_instances
        ]

    def get_all_by_transaction_id(self, transaction_id: str, user_id: int, filters: dict = {}) -> list["SubTransactionDomain"]:
        sub_transaction_instances = self.queryset.filter(transaction_id=transaction_id, transaction__user_id=user_id, **filters)
        return [
            self.sub_transaction_factory.build_from_model(sub_transaction_instance)
            for sub_transaction_instance in sub_transaction_instances
        ]
    
    def get_all_by_transaction_ids(self, transaction_ids: list[str]) -> list["SubTransactionDomain"]:
        sub_transaction_instances = self.queryset.filter(transaction_id__in=transaction_ids)
        return [
            self.sub_transaction_factory.build_from_model(sub_transaction_instance)
            for sub_transaction_instance in sub_transaction_instances
        ]
    
    def get_all_by_actor_ids(self, actor_ids: list[str], due_date: str = None) -> list["SubTransactionDomain"]:
        sub_transaction_instances = self.queryset.filter(actor_id__in=actor_ids)

        if due_date:
            date = datetime.strptime(due_date, "%Y-%m-%d")
            sub_transaction_instances = sub_transaction_instances.filter(
                transaction__due_date__month=date.month, 
                transaction__due_date__year=date.year
            )

        return [
            self.sub_transaction_factory.build_from_model(sub_transaction_instance)
            for sub_transaction_instance in sub_transaction_instances
        ]
    
    def filter_by_actor_ids(self, actor_ids: list[str], filters: dict = {}) -> list["SubTransactionDomain"]:
        sub_transaction_instances = self.queryset.filter(actor_id__in=actor_ids, **filters)
        return [
            self.sub_transaction_factory.build_from_model(sub_transaction_instance)
            for sub_transaction_instance in sub_transaction_instances
        ]
    
    def filter_by_actor_id(self, actor_id: str, filters: dict = {}) -> list["SubTransactionDomain"]:
        sub_transaction_instances = self.queryset.filter(actor_id=actor_id, **filters)
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
            user_provided_description=sub_transaction.user_provided_description,
        )
        return self.sub_transaction_factory.build_from_model(sub_transaction_instance)
    
    def create_many(self, sub_transactions: list["SubTransactionDomain"]) -> list["SubTransactionDomain"]:
        return [
            self.create(sub_transaction) for sub_transaction in sub_transactions
        ]
    
    def update(self, sub_transaction: "SubTransactionDomain") -> "SubTransactionDomain":
        sub_transaction_instance = self.queryset.get(id=sub_transaction.id)
        sub_transaction_instance.date = sub_transaction.date
        sub_transaction_instance.description = sub_transaction.description
        sub_transaction_instance.amount = sub_transaction.amount
        sub_transaction_instance.installment_info = sub_transaction.installment_info
        sub_transaction_instance.transaction_id = sub_transaction.transaction.id
        sub_transaction_instance.actor_id = sub_transaction.actor_id 
        sub_transaction_instance.user_provided_description = sub_transaction.user_provided_description
        sub_transaction_instance.save()
        return self.sub_transaction_factory.build_from_model(sub_transaction_instance)
    
    def update_paid_at(self, sub_transaction: "SubTransactionDomain"):
        self.queryset.filter(id=sub_transaction.id).update(paid_at=sub_transaction.paid_at)
    
    def delete(self, sub_transaction_id: str):
        self.queryset.filter(id=sub_transaction_id).update(deleted_at=timezone.now())

    def delete_many(self, sub_transactions: list["SubTransactionDomain"]):
        sub_transaction_ids = [sub_transaction.id for sub_transaction in sub_transactions]
        self.queryset.filter(id__in=sub_transaction_ids).update(deleted_at=timezone.now())

    def duplicate(self, sub_transaction_id: str, extra_data: dict = {}) -> "SubTransactionDomain":
        sub_transaction_instance = self.queryset.get(id=sub_transaction_id)
        sub_transaction_instance.pk = None

        for key, value in extra_data.items():
            setattr(sub_transaction_instance, key, value)
        
        sub_transaction_instance.save()
        return self.sub_transaction_factory.build_from_model(sub_transaction_instance)
