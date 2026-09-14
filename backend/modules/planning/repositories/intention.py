from django.utils import timezone

from modules.planning.domains.intention import PurchaseIntentionDomain
from modules.planning.factories.intention import PurchaseIntentionFactory
from modules.planning.models import PurchaseIntention


class PurchaseIntentionRepository:
    def __init__(self, model: PurchaseIntention, intention_factory: PurchaseIntentionFactory):
        self.model = model
        self.intention_factory = intention_factory

    @property
    def queryset(self):
        return (
            self.model.objects
                .order_by("month", "id")
                .exclude(deleted_at__isnull=False)
        )

    def get(self, intention_id: int, user_id: int) -> "PurchaseIntentionDomain":
        instance = self.queryset.get(id=intention_id, user_id=user_id)
        return self.intention_factory.build_from_model(instance)

    def filter(self, filters: dict) -> list["PurchaseIntentionDomain"]:
        instances = self.queryset.filter(**filters)
        return [self.intention_factory.build_from_model(instance) for instance in instances]

    def create(self, intention: "PurchaseIntentionDomain") -> "PurchaseIntentionDomain":
        instance = self.model.objects.create(
            name=intention.name,
            amount=intention.amount,
            month=intention.month,
            status=intention.status,
            transaction_id=intention.transaction_id,
            user_id=intention.user_id,
        )
        instance.refresh_from_db()
        return self.intention_factory.build_from_model(instance)

    def update(self, intention: "PurchaseIntentionDomain") -> "PurchaseIntentionDomain":
        instance = self.queryset.get(id=intention.id, user_id=intention.user_id)
        instance.name = intention.name
        instance.amount = intention.amount
        instance.month = intention.month
        instance.status = intention.status
        instance.transaction_id = intention.transaction_id
        instance.save()
        return self.intention_factory.build_from_model(instance)

    def delete(self, intention_id: int, user_id: int):
        self.queryset.filter(id=intention_id, user_id=user_id).update(deleted_at=timezone.now())
