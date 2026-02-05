from typing import TYPE_CHECKING
from django.utils import timezone

if TYPE_CHECKING:
    from modules.transactions.domains.sub_transaction import SubTransactionDomain


class TransactionDomain:
    def __init__(
        self,
        due_date: str = None,
        total_amount: float = None,
        transaction_identifier: str = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        transaction_type: str = None,
        is_salary: bool = False,
        user_id: int = None,
        sub_transactions: list["SubTransactionDomain"] = [],
        is_recurrent: bool = False,
        installment_number: int = None,
        main_transaction: "TransactionDomain" = None,
        recurrence_count: int = None,
        amount_from_actor: float = None,
        file_id: int = None,
        paid_at: str = None,
        subtransactions_paid: bool = None,
    ):
        self.due_date = due_date
        self.total_amount = total_amount
        self.transaction_identifier = transaction_identifier
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.transaction_type = transaction_type
        self.is_salary = is_salary
        self.user_id = user_id
        self.sub_transactions = sub_transactions
        self.is_recurrent = is_recurrent
        self.installment_number = installment_number
        self.main_transaction = main_transaction
        self.recurrence_count = recurrence_count
        self.amount_from_actor = amount_from_actor
        self.file_id = file_id
        self.paid_at = paid_at
        self.subtransactions_paid = subtransactions_paid
        self.is_paid = paid_at is not None

    def is_paying(self):
        return self.paid_at is None
    
    def unpay(self):
        self.paid_at = None

    def pay(self):
        self.paid_at = timezone.now().date()

    def update_amount(self, total_amount: float):
        self.total_amount = total_amount

    def set_sub_transactions(self, sub_transactions: list["SubTransactionDomain"]):
        self.sub_transactions = sub_transactions

    def update(self, data: dict):
        self.due_date = data.get("due_date", self.due_date)
        self.total_amount = data.get("total_amount", self.total_amount)
        self.transaction_identifier = data.get("transaction_identifier", self.transaction_identifier)
        self.transaction_type = data.get("transaction_type", self.transaction_type)
        self.is_salary = data.get("is_salary", self.is_salary)


