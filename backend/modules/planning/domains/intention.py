from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.transactions.domains import TransactionDomain


class PurchaseIntentionDomain:
    def __init__(
        self,
        name: str = None,
        amount: float = None,
        month: str = None,
        status: str = "planned",
        transaction_id: int = None,
        id: int = None,
        user_id: int = None,
        created_at: str = None,
        updated_at: str = None,
        deleted_at: str = None,
    ):
        self.name = name
        self.amount = amount
        self.month = month
        self.status = status
        self.transaction_id = transaction_id
        self.id = id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at

    def update(self, data: dict):
        self.name = data.get("name", self.name)
        self.amount = data.get("amount", self.amount)
        self.month = data.get("month", self.month)
        self.status = data.get("status", self.status)
        self.transaction_id = data.get("transaction_id", self.transaction_id)
