from modules.transactions.domains import SubTransactionDomain
from modules.transactions.serializers import ActorSerializer


class SubTransactionSerializer:
    def __init__(self, actor_serializer: ActorSerializer):
        self.actor_serializer = actor_serializer

    def serialize(self, sub_transaction: "SubTransactionDomain", include_actor: bool = True) -> dict:
        return {
            "id": sub_transaction.id,
            "date": sub_transaction.date,
            "description": sub_transaction.description,
            "amount": sub_transaction.amount,
            "actor": self.actor_serializer.serialize(sub_transaction.actor) if include_actor and sub_transaction.actor else None,
            "transaction_id": sub_transaction.transaction.id,
            "transaction_identifier": sub_transaction.transaction.transaction_identifier,
            "installment_info": sub_transaction.installment_info,
            "created_at": sub_transaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": sub_transaction.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "user_provided_description": sub_transaction.user_provided_description,
        }

    def serialize_many(self, sub_transactions: list["SubTransactionDomain"], include_actor: bool = True) -> list[dict]:
        return [self.serialize(sub_transaction, include_actor) for sub_transaction in sub_transactions]
