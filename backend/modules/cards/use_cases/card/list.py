from modules.cards.repositories.card import CardRepository
from modules.cards.serializers.card import CardSerializer


class ListCardsUseCase:
    def __init__(self, card_repository: CardRepository, card_serializer: CardSerializer):
        self.card_repository = card_repository
        self.card_serializer = card_serializer

    def execute(self, user_id: int) -> list[dict]:
        cards = self.card_repository.get_all(user_id)
        return [self.card_serializer.serialize(card) for card in cards]
