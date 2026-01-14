from modules.transactions.domains import SubTransactionDomain
from modules.transactions.serializers import ActorSerializer


class SubTransactionSerializer:
    def __init__(self, actor_serializer: ActorSerializer):
        self.actor_serializer = actor_serializer

    def serialize(self, sub_transaction: "SubTransactionDomain") -> dict:
        return {
            "id": sub_transaction.id,
            "date": sub_transaction.date,
            "description": sub_transaction.description,
            "amount": sub_transaction.amount,
            "actor": self.actor_serializer.serialize(sub_transaction.actor) if sub_transaction.actor else None,
            "transaction_id": sub_transaction.transaction.id,
            "installment_info": sub_transaction.installment_info,
            "created_at": sub_transaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": sub_transaction.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
