from modules.transactions.domains import SubTransactionDomain, ActorDomain, TransactionDomain
from modules.transactions.factories import ActorFactory, TransactionFactory
from modules.transactions.models import SubTransaction


class SubTransactionFactory:
    def __init__(
        self,
        transaction_factory: TransactionFactory,
        actor_factory: ActorFactory,
    ):
        self.transaction_factory = transaction_factory
        self.actor_factory = actor_factory

    def build_from_model(self, model: SubTransaction) -> SubTransactionDomain:
        actor = self.actor_factory.build_from_model(model.actor) if model.actor else None
        return SubTransactionDomain(
            date=model.date,
            description=model.description,
            amount=model.amount,
            installment_info=model.installment_info,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            transaction=self.transaction_factory.build_from_model(model.transaction),
            actor=actor,
            user_provided_description=model.user_provided_description,
            paid_at=model.paid_at,
        )
    
    def build(self, data: dict, transaction: TransactionDomain, actor: ActorDomain = None) -> SubTransactionDomain:
        return SubTransactionDomain(
            description=data["description"],
            amount=data["amount"],
            installment_info=data.get("installment_info"),
            transaction=transaction,
            actor=actor,
            user_provided_description=data.get("user_provided_description", None),
        )
    
    def build_from_transaction(self, transaction: TransactionDomain, installment = "1/1") -> SubTransactionDomain:
        return SubTransactionDomain(
            date=transaction.due_date,
            amount=transaction.total_amount,
            transaction=transaction,
            description=transaction.transaction_identifier,
            installment_info=installment,
        )
