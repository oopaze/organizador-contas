from modules.cards.repositories.card import CardRepository
from modules.cards.serializers.card import CardSerializer


class UpdateCardUseCase:
    def __init__(self, card_repository: CardRepository, card_serializer: CardSerializer):
        self.card_repository = card_repository
        self.card_serializer = card_serializer

    def execute(self, card_id: int, data: dict, user_id: int) -> dict:
        card = self.card_repository.get(card_id, user_id)

        name = (data.get("name", card.name) or "").strip()
        if not name:
            raise ValueError("name é obrigatório")
        try:
            due_day = int(data.get("due_day", card.due_day))
        except (TypeError, ValueError):
            raise ValueError("due_day deve ser um número inteiro")
        if due_day < 1 or due_day > 31:
            raise ValueError("due_day deve estar entre 1 e 31")

        card.update({"name": name, "due_day": due_day})
        updated = self.card_repository.update(card)
        return self.card_serializer.serialize(updated)
