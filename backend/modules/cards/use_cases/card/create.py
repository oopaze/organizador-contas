from modules.cards.factories.card import CardFactory
from modules.cards.repositories.card import CardRepository
from modules.cards.serializers.card import CardSerializer


class CreateCardUseCase:
    def __init__(self, card_repository: CardRepository, card_factory: CardFactory, card_serializer: CardSerializer):
        self.card_repository = card_repository
        self.card_factory = card_factory
        self.card_serializer = card_serializer

    def execute(self, data: dict, user_id: int) -> dict:
        name = (data.get("name") or "").strip()
        if not name:
            raise ValueError("name é obrigatório")
        try:
            due_day = int(data.get("due_day", 1))
        except (TypeError, ValueError):
            raise ValueError("due_day deve ser um número inteiro")
        if due_day < 1 or due_day > 31:
            raise ValueError("due_day deve estar entre 1 e 31")

        card = self.card_factory.build(
            {**data, "name": name, "due_day": due_day, "user_id": user_id}
        )
        created = self.card_repository.create(card)
        return self.card_serializer.serialize(created)
