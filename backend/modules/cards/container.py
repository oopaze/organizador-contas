from dependency_injector import containers, providers

from modules.cards.factories.card import CardFactory
from modules.cards.models import Card
from modules.cards.repositories.card import CardRepository
from modules.cards.serializers.card import CardSerializer
from modules.cards.use_cases import (
    CreateCardUseCase,
    ListCardsUseCase,
    SetCardActiveUseCase,
    UpdateCardUseCase,
)


class CardsContainer(containers.DeclarativeContainer):
    card_factory = providers.Factory(CardFactory)
    card_repository = providers.Factory(CardRepository, model=Card, card_factory=card_factory)
    card_serializer = providers.Factory(CardSerializer)

    create_card_use_case = providers.Factory(
        CreateCardUseCase, card_repository=card_repository, card_factory=card_factory, card_serializer=card_serializer
    )
    list_cards_use_case = providers.Factory(
        ListCardsUseCase, card_repository=card_repository, card_serializer=card_serializer
    )
    update_card_use_case = providers.Factory(
        UpdateCardUseCase, card_repository=card_repository, card_serializer=card_serializer
    )
    set_card_active_use_case = providers.Factory(
        SetCardActiveUseCase, card_repository=card_repository, card_serializer=card_serializer
    )
