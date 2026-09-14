from modules.planning.repositories.intention import PurchaseIntentionRepository
from modules.planning.serializers.intention import PurchaseIntentionSerializer
from modules.transactions.container import TransactionsContainer


class ConvertPurchaseIntentionUseCase:
    """Turns a planned intention into a real (unpaid) transaction.

    The intention month becomes the transaction due date; the created
    transaction id is stored on the intention and its status becomes
    ``bought``.
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

        transaction = self.transactions_container.create_transaction_use_case().execute(
            {
                "transaction_identifier": intention.name,
                "total_amount": str(intention.amount),
                "due_date": intention.month.isoformat(),
                "transaction_type": "outgoing",
                "category": data.get("category"),
                "is_salary": False,
                "is_recurrent": False,
                "user_id": user_id,
                "paid_at": data.get("paid_at"),
            }
        )

        intention.update({"status": "bought", "transaction_id": transaction["id"]})
        updated = self.intention_repository.update(intention)
        return self.intention_serializer.serialize(updated)
