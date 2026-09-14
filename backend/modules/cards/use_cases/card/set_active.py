from modules.cards.repositories.card import CardRepository
from modules.cards.serializers.card import CardSerializer


class SetCardActiveUseCase:
    def __init__(self, card_repository: CardRepository, card_serializer: CardSerializer):
        self.card_repository = card_repository
        self.card_serializer = card_serializer

    def execute(self, card_id: int, is_active: bool, user_id: int) -> dict:
        card = self.card_repository.get(card_id, user_id)
        card.update({"is_active": bool(is_active)})
        updated = self.card_repository.update(card)
        return self.card_serializer.serialize(updated)
