from modules.cards.factories.card import CardFactory
from modules.cards.repositories.card import CardRepository
from modules.cards.serializers.card import CardSerializer


class CreateCardUseCase:
    def __init__(self, card_repository: CardRepository, card_factory: CardFactory, card_serializer: CardSerializer):
        self.card_repository = card_repository
        self.card_factory = card_factory
        self.card_serializer = card_serializer

    def execute(self, data: dict, user_id: int) -> dict:
        card = self.card_factory.build({**data, "user_id": user_id})
        created = self.card_repository.create(card)
        return self.card_serializer.serialize(created)
