from django.utils import timezone

from modules.cards.domains.card import CardDomain
from modules.cards.factories.card import CardFactory
from modules.cards.models import Card


class CardRepository:
    def __init__(self, model: Card, card_factory: CardFactory):
        self.model = model
        self.card_factory = card_factory

    @property
    def queryset(self):
        return (
            self.model.objects
                .order_by("name")
                .exclude(deleted_at__isnull=False)
        )

    def get(self, card_id: int, user_id: int) -> "CardDomain":
        instance = self.queryset.get(id=card_id, user_id=user_id)
        return self.card_factory.build_from_model(instance)

    def get_by_name(self, user_id: int, name: str) -> "CardDomain | None":
        instance = (
            self.queryset
            .filter(user_id=user_id, name__iexact=(name or "").strip())
            .first()
        )
        if instance is None:
            return None
        return self.card_factory.build_from_model(instance)

    def get_all(self, user_id: int, only_active: bool = False) -> list["CardDomain"]:
        filters = {"user_id": user_id}
        if only_active:
            filters["is_active"] = True
        instances = self.queryset.filter(**filters)
        return [self.card_factory.build_from_model(instance) for instance in instances]

    def create(self, card: "CardDomain") -> "CardDomain":
        instance = self.model.objects.create(
            name=card.name,
            due_day=card.due_day,
            is_active=card.is_active,
            user_id=card.user_id,
        )
        instance.refresh_from_db()
        return self.card_factory.build_from_model(instance)

    def update(self, card: "CardDomain") -> "CardDomain":
        instance = self.queryset.get(id=card.id, user_id=card.user_id)
        instance.name = card.name
        instance.due_day = card.due_day
        instance.is_active = card.is_active
        instance.save()
        return self.card_factory.build_from_model(instance)

    def delete(self, card_id: int, user_id: int):
        self.queryset.filter(id=card_id, user_id=user_id).update(deleted_at=timezone.now())
