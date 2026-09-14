from modules.cards.domains.card import CardDomain
from modules.cards.models import Card


class CardFactory:
    def build_from_model(self, model: Card) -> CardDomain:
        return CardDomain(
            id=model.id,
            name=model.name,
            due_day=model.due_day,
            is_active=model.is_active,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    def build(self, data: dict) -> CardDomain:
        return CardDomain(
            name=data["name"],
            due_day=data.get("due_day", 1),
            is_active=data.get("is_active", True),
            user_id=data["user_id"],
        )
