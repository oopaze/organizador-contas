from dependency_injector import containers, providers

from modules.planning.factories.intention import PurchaseIntentionFactory
from modules.planning.models import PurchaseIntention
from modules.planning.repositories.intention import PurchaseIntentionRepository
from modules.planning.serializers.intention import PurchaseIntentionSerializer
from modules.planning.use_cases import (
    ConvertPurchaseIntentionUseCase,
    CreatePurchaseIntentionUseCase,
    DeletePurchaseIntentionUseCase,
    ListPurchaseIntentionsUseCase,
    UpdatePurchaseIntentionUseCase,
)
from modules.transactions.container import TransactionsContainer


class PlanningContainer(containers.DeclarativeContainer):
    # FACTORIES
    intention_factory = providers.Factory(PurchaseIntentionFactory)

    # REPOSITORIES
    intention_repository = providers.Factory(
        PurchaseIntentionRepository,
        model=PurchaseIntention,
        intention_factory=intention_factory,
    )

    # SERIALIZERS
    intention_serializer = providers.Factory(PurchaseIntentionSerializer)

    # Cross-module: converting an intention creates a real transaction
    transactions_container = providers.Singleton(TransactionsContainer)

    # USE CASES
    create_intention_use_case = providers.Factory(
        CreatePurchaseIntentionUseCase,
        intention_repository=intention_repository,
        intention_factory=intention_factory,
        intention_serializer=intention_serializer,
    )

    list_intentions_use_case = providers.Factory(
        ListPurchaseIntentionsUseCase,
        intention_repository=intention_repository,
        intention_serializer=intention_serializer,
    )

    update_intention_use_case = providers.Factory(
        UpdatePurchaseIntentionUseCase,
        intention_repository=intention_repository,
        intention_serializer=intention_serializer,
    )

    delete_intention_use_case = providers.Factory(
        DeletePurchaseIntentionUseCase,
        intention_repository=intention_repository,
    )

    convert_intention_use_case = providers.Factory(
        ConvertPurchaseIntentionUseCase,
        intention_repository=intention_repository,
        intention_serializer=intention_serializer,
        transactions_container=transactions_container,
    )
