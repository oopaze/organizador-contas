from modules.transactions.domains import ActorDomain, TransactionDomain


class SubTransactionDomain:
    def __init__(
        self,
        date: str = None,
        description: str = None,
        amount: float = None,
        installment_info: str = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        transaction: "TransactionDomain" = None,
        actor: "ActorDomain" = None,
    ):
        self.date = date
        self.description = description
        self.amount = amount
        self.installment_info = installment_info
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.transaction = transaction
        self.actor = actor
    
    def update(self, data: dict):
        self.date = data.get("date", self.date)
        self.description = data.get("description", self.description)
        self.amount = data.get("amount", self.amount)
        self.installment_info = data.get("installment_info", self.installment_info)
        self.transaction = data.get("transaction", self.transaction)
        self.actor = data.get("actor", self.actor)
