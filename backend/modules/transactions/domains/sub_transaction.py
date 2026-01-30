from decimal import Decimal

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
        user_provided_description: str = "",
    ):
        self.date = date
        self.description = description
        self.installment_info = installment_info
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.transaction = transaction
        self.actor = actor
        self.actor_id = actor.id if isinstance(actor, ActorDomain) else actor
        self.user_provided_description = user_provided_description
        self.amount = self.format_money(amount)
    
    def update(self, data: dict):
        self.date = data.get("date", self.date)
        self.description = data.get("description", self.description)
        self.amount = self.format_money(data.get("amount", self.amount))
        self.installment_info = data.get("installment_info", self.installment_info)
        self.transaction = data.get("transaction", self.transaction)
        self.actor = data.get("actor", self.actor)
        self.actor_id = data.get("actor_id", self.actor_id)
        self.user_provided_description = data.get("user_provided_description", self.user_provided_description)

    def format_money(self, value):
        if isinstance(value, (float, int)):
            return Decimal(value)
        if isinstance(value, str):
            try:
                return Decimal(value.replace(',', ''))
            except:
                pass

        return value
