from modules.cards.domains.card import CardDomain


class CardSerializer:
    def serialize(self, card: "CardDomain") -> dict:
        return {
            "id": card.id,
            "name": card.name,
            "due_day": card.due_day,
            "is_active": card.is_active,
        }
