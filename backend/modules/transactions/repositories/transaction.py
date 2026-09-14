from django.utils import timezone
from django.db.models import Case, When, Value, BooleanField, Exists, OuterRef

from modules.transactions.domains import TransactionDomain
from modules.transactions.factories.transaction import TransactionFactory
from modules.transactions.models import Transaction, SubTransaction


class TransactionRepository:
    def __init__(self, model: Transaction, transaction_factory: TransactionFactory):
        self.model = model
        self.transaction_factory = transaction_factory

    @property
    def queryset(self):
        return (
            self.model.objects
                .order_by("id")
                .exclude(deleted_at__isnull=False)
                .prefetch_related("sub_transactions")
        )

    def _annotate_subtransactions_paid(self, queryset):
        has_subtransactions = SubTransaction.objects.filter(transaction=OuterRef('pk'))
        unpaid_subtransactions = SubTransaction.objects.filter(
            transaction=OuterRef('pk'),
            paid_at__isnull=True
        )

        return queryset.annotate(
            subtransactions_paid=Case(
                When(
                    Exists(has_subtransactions),
                    then=~Exists(unpaid_subtransactions),
                ),
                default=Value(False),
                output_field=BooleanField(),
            )
        )

    def filter(self, filters: dict) -> list["TransactionDomain"]:
        queryset = self._annotate_subtransactions_paid(self.queryset.filter(**filters))
        return [self.transaction_factory.build_from_model(transaction) for transaction in queryset]

    def get(self, transaction_id: str, user_id: int) -> "TransactionDomain":
        transaction_instance = self.queryset.get(id=transaction_id, user_id=user_id)
        return self.transaction_factory.build_from_model(transaction_instance)
    
    def get_children_transactions(self, transaction_id: str, user_id: int) -> list["TransactionDomain"]:
        transaction_instances = self.queryset.filter(main_transaction_id=transaction_id, user_id=user_id)
        return [self.transaction_factory.build_from_model(transaction) for transaction in transaction_instances]
    
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
            category=transaction.category,
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
        transaction_instance.category = transaction.category
        transaction_instance.save()
        return self.transaction_factory.build_from_model(transaction_instance)
    
    def update_paid_at(self, transaction: "TransactionDomain"):
        self.queryset.filter(id=transaction.id).update(paid_at=transaction.paid_at)
    
    def update_many(self, transactions: list["TransactionDomain"]) -> list["TransactionDomain"]:
        return [self.update(transaction) for transaction in transactions]
    
    def delete(self, transaction_id: str, user_id: int):
        self.queryset.filter(id=transaction_id, user_id=user_id).update(deleted_at=timezone.now())

    def delete_many(self, transactions: list["TransactionDomain"]):
        transaction_ids = [transaction.id for transaction in transactions]
        self.queryset.filter(id__in=transaction_ids).update(deleted_at=timezone.now())


