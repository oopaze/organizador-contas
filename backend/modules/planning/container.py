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
    ProjectionUseCase,
    UpdatePurchaseIntentionUseCase,
)
from modules.transactions.container import TransactionsContainer
from modules.userdata.factories import ProfileFactory
from modules.userdata.models import Profile
from modules.userdata.repositories.profile import ProfileRepository


class PlanningContainer(containers.DeclarativeContainer):
    # DEPENDENCIES (AI bits injected from views for intention conversion)
    ask_use_case = providers.Dependency()
    ai_call_repository = providers.Dependency()

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

    profile_repository = providers.Factory(
        ProfileRepository, model=Profile, profile_factory=providers.Factory(ProfileFactory)
    )

    # Cross-module: converting an intention creates a real transaction
    transactions_container = providers.Container(
        TransactionsContainer,
        ask_use_case=ask_use_case,
        ai_call_repository=ai_call_repository,
    )

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

    projection_use_case = providers.Factory(
        ProjectionUseCase,
        intention_repository=intention_repository,
        profile_repository=profile_repository,
        sub_transaction_repository=transactions_container.sub_transaction_repository,
    )
