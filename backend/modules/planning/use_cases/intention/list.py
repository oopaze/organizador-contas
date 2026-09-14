from modules.planning.repositories.intention import PurchaseIntentionRepository
from modules.planning.serializers.intention import PurchaseIntentionSerializer


class ListPurchaseIntentionsUseCase:
    def __init__(
        self,
        intention_repository: PurchaseIntentionRepository,
        intention_serializer: PurchaseIntentionSerializer,
    ):
        self.intention_repository = intention_repository
        self.intention_serializer = intention_serializer

    def execute(
        self, user_id: int, month: str = None, start: str = None, end: str = None, status: str = None
    ) -> list[dict]:
        filters = {"user_id": user_id}
        if month:
            year, month_number = str(month).split("-")
            filters["month__year"] = int(year)
            filters["month__month"] = int(month_number)
        if start:
            filters["month__gte"] = start
        if end:
            filters["month__lte"] = end
        if status:
            filters["status"] = status

        intentions = self.intention_repository.filter(filters)
        return [self.intention_serializer.serialize(intention) for intention in intentions]
