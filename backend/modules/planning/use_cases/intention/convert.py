from modules.planning.repositories.intention import PurchaseIntentionRepository
from modules.planning.serializers.intention import PurchaseIntentionSerializer
from modules.transactions.container import TransactionsContainer


class ConvertPurchaseIntentionUseCase:
    """Turns a planned intention into real (unpaid) transaction(s).

    Uses the quick-add flow, so an installment intention creates one
    transaction per month. Once converted the intention is `bought` and
    stops being counted as an intention (and can no longer be deleted).
    """

    def __init__(
        self,
        intention_repository: PurchaseIntentionRepository,
        intention_serializer: PurchaseIntentionSerializer,
        transactions_container: TransactionsContainer,
    ):
        self.intention_repository = intention_repository
        self.intention_serializer = intention_serializer
        self.transactions_container = transactions_container

    def execute(self, intention_id: int, data: dict, user_id: int) -> dict:
        intention = self.intention_repository.get(intention_id, user_id)
        if intention.status == "bought":
            raise ValueError("Intenção já virou transação")

        result = self.transactions_container.quick_add_transaction_use_case().execute(
            {
                "direction": "outgoing",
                "payment_method": "cash",
                "amount": str(intention.amount),
                "description": intention.name,
                "date": intention.month.isoformat(),
                "installments": intention.installments,
                "is_paid": False,
                "category": data.get("category"),
                "actor_id": data.get("actor_id"),
            },
            user_id,
        )

        intention.update(
            {
                "status": "bought",
                "transaction_id": result["transaction"]["id"],
            }
        )
        updated = self.intention_repository.update(intention)
        return self.intention_serializer.serialize(updated)
