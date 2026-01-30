from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.transactions.domains.sub_transaction import SubTransactionDomain


class ActorDomain:
    def __init__(
        self,
        name: str = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        user_id: int = None,
        sub_transactions: list["SubTransactionDomain"] = [],
    ):
        self.name = name
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.user_id = user_id
        self.sub_transactions = sub_transactions

    def update(self, name: str):
        self.name = name

    def set_sub_transactions(self, sub_transactions: list["SubTransactionDomain"]):
        self.sub_transactions = sub_transactions

    def get_total_spent(self) -> float:
        return sum(sub_transaction.amount for sub_transaction in self.sub_transactions) if self.sub_transactions else 0

    @property
    def total_spent(self) -> float:
        return self.get_total_spent()
    
    def __lt__(self, other):
        return self.total_spent < other.total_spent
    
    def __gt__(self, other):
        return self.total_spent > other.total_spent
