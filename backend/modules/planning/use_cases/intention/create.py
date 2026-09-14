from modules.planning.factories.intention import PurchaseIntentionFactory
from modules.planning.repositories.intention import PurchaseIntentionRepository
from modules.planning.serializers.intention import PurchaseIntentionSerializer


class CreatePurchaseIntentionUseCase:
    def __init__(
        self,
        intention_repository: PurchaseIntentionRepository,
        intention_factory: PurchaseIntentionFactory,
        intention_serializer: PurchaseIntentionSerializer,
    ):
        self.intention_repository = intention_repository
        self.intention_factory = intention_factory
        self.intention_serializer = intention_serializer

    def execute(self, data: dict, user_id: int) -> dict:
        intention = self.intention_factory.build({**data, "user_id": user_id})
        created = self.intention_repository.create(intention)
        return self.intention_serializer.serialize(created)
