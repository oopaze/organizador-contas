from modules.planning.repositories.intention import PurchaseIntentionRepository
from modules.planning.serializers.intention import PurchaseIntentionSerializer


class UpdatePurchaseIntentionUseCase:
    def __init__(
        self,
        intention_repository: PurchaseIntentionRepository,
        intention_serializer: PurchaseIntentionSerializer,
    ):
        self.intention_repository = intention_repository
        self.intention_serializer = intention_serializer

    def execute(self, intention_id: int, data: dict, user_id: int) -> dict:
        intention = self.intention_repository.get(intention_id, user_id)
        new_status = data.get("status")
        if intention.status == "bought" and new_status and new_status != "bought":
            raise ValueError("Intenção já virou transação")
        intention.update(data)
        updated = self.intention_repository.update(intention)
        return self.intention_serializer.serialize(updated)
