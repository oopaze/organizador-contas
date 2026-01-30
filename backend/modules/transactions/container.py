from dependency_injector import containers, providers

from modules.transactions.factories import ActorFactory, TransactionFactory, SubTransactionFactory
from modules.transactions.factories.actor import ActorFactory
from modules.transactions.models import Actor, Transaction, SubTransaction
from modules.transactions.repositories import ActorRepository, TransactionRepository, SubTransactionRepository
from modules.transactions.serializers import ActorSerializer, TransactionSerializer, SubTransactionSerializer
from modules.transactions.factories import ActorFactory, TransactionFactory, SubTransactionFactory
from modules.transactions.use_cases import (
    GetToolsForAIUseCase,
    CreateActorUseCase,
    DeleteActorUseCase,
    GetActorUseCase,
    ListActorsUseCase,
    UpdateActorUseCase,
    ActorStatsUseCase,
    CreateTransactionUseCase,
    DeleteTransactionUseCase,
    GetTransactionUseCase,
    ListTransactionsUseCase,
    UpdateTransactionUseCase,
    TransactionStatsUseCase,
    CreateSubTransactionUseCase,
    DeleteSubTransactionUseCase,
    GetSubTransactionUseCase,
    ListSubTransactionsUseCase,
    UpdateSubTransactionUseCase,
    GetActorsToolUseCase,
    GetActorDetailToolUseCase,
    GetActorStatsToolUseCase,
    GetSubTransactionsFromTransactionToolUseCase,
    GetUserGeneralStatsToolUseCase,
    GetTransactionsToolUseCase,
)


class TransactionsContainer(containers.DeclarativeContainer):
    # DEPENDENCIES
    user_id = providers.Dependency()

    # SERIALIZERS
    actor_serializer = providers.Factory(ActorSerializer)
    sub_transaction_serializer = providers.Factory(
        SubTransactionSerializer, actor_serializer=actor_serializer,
    )
    transaction_serializer = providers.Factory(
        TransactionSerializer, sub_transaction_serializer=sub_transaction_serializer,
    )

    # FACTORIES
    actor_factory = providers.Factory(ActorFactory)
    transaction_factory = providers.Factory(TransactionFactory)
    sub_transaction_factory = providers.Factory(
        SubTransactionFactory,
        actor_factory=actor_factory,
        transaction_factory=transaction_factory,
    )

    # REPOSITORIES
    actor_repository = providers.Factory(ActorRepository, model=Actor, actor_factory=actor_factory)
    transaction_repository = providers.Factory(TransactionRepository, model=Transaction, transaction_factory=transaction_factory)
    sub_transaction_repository = providers.Factory(SubTransactionRepository, model=SubTransaction, sub_transaction_factory=sub_transaction_factory)

    # USE CASES
    list_actors_use_case = providers.Factory(
        ListActorsUseCase,
        actor_repository=actor_repository,
        actor_serializer=actor_serializer,
        sub_transaction_repository=sub_transaction_repository,
        sub_transaction_serializer=sub_transaction_serializer,
    )

    get_actor_use_case = providers.Factory(
        GetActorUseCase,
        actor_repository=actor_repository,
        actor_serializer=actor_serializer,
        sub_transaction_repository=sub_transaction_repository,
        sub_transaction_serializer=sub_transaction_serializer,
    )

    create_actor_use_case = providers.Factory(
        CreateActorUseCase,
        actor_repository=actor_repository,
        actor_serializer=actor_serializer,
        actor_factory=actor_factory,
    )

    update_actor_use_case = providers.Factory(
        UpdateActorUseCase,
        actor_repository=actor_repository,
        actor_serializer=actor_serializer,
    )

    delete_actor_use_case = providers.Factory(
        DeleteActorUseCase,
        actor_repository=actor_repository,
    )

    actor_stats_use_case = providers.Factory(
        ActorStatsUseCase,
        actor_repository=actor_repository,
        sub_transaction_repository=sub_transaction_repository,
    )

    list_transactions_use_case = providers.Factory(
        ListTransactionsUseCase,
        transaction_repository=transaction_repository,
        transaction_serializer=transaction_serializer,
    )

    get_transaction_use_case = providers.Factory(
        GetTransactionUseCase,
        transaction_repository=transaction_repository,
        transaction_serializer=transaction_serializer,
        sub_transaction_repository=sub_transaction_repository,
    )

    create_transaction_use_case = providers.Factory(
        CreateTransactionUseCase,
        transaction_repository=transaction_repository,
        transaction_serializer=transaction_serializer,
        transaction_factory=transaction_factory,
        sub_transaction_factory=sub_transaction_factory,
        sub_transaction_repository=sub_transaction_repository,
    )

    update_transaction_use_case = providers.Factory(
        UpdateTransactionUseCase,
        transaction_repository=transaction_repository,
        transaction_serializer=transaction_serializer,
        sub_transaction_repository=sub_transaction_repository,
    )

    delete_transaction_use_case = providers.Factory(
        DeleteTransactionUseCase,
        transaction_repository=transaction_repository,
    )

    transaction_stats_use_case = providers.Factory(
        TransactionStatsUseCase,
        transaction_repository=transaction_repository,
        sub_transaction_repository=sub_transaction_repository,
    )

    create_sub_transaction_use_case = providers.Factory(
        CreateSubTransactionUseCase,
        transaction_repository=transaction_repository,
        actor_repository=actor_repository,
        sub_transaction_repository=sub_transaction_repository,
        sub_transaction_serializer=sub_transaction_serializer,
        sub_transaction_factory=sub_transaction_factory,
    )

    get_sub_transaction_use_case = providers.Factory(
        GetSubTransactionUseCase,
        sub_transaction_repository=sub_transaction_repository,
        sub_transaction_serializer=sub_transaction_serializer,
    )

    list_sub_transactions_use_case = providers.Factory(
        ListSubTransactionsUseCase,
        sub_transaction_repository=sub_transaction_repository,
        sub_transaction_serializer=sub_transaction_serializer,
    )

    update_sub_transaction_use_case = providers.Factory(
        UpdateSubTransactionUseCase,
        sub_transaction_repository=sub_transaction_repository,
        sub_transaction_serializer=sub_transaction_serializer,
        actor_repository=actor_repository,
    )

    delete_sub_transaction_use_case = providers.Factory(
        DeleteSubTransactionUseCase,
        sub_transaction_repository=sub_transaction_repository,
    )

    get_actors_tool_use_case = providers.Factory(
        GetActorsToolUseCase,
        actor_repository=actor_repository,
        actor_serializer=actor_serializer,
        sub_transaction_repository=sub_transaction_repository,
        user_id=user_id,
    )

    get_actor_detail_tool_use_case = providers.Factory(
        GetActorDetailToolUseCase,
        actor_repository=actor_repository,
        actor_serializer=actor_serializer,
        sub_transaction_repository=sub_transaction_repository,
        sub_transaction_serializer=sub_transaction_serializer,
        user_id=user_id,
    )

    get_actor_stats_tool_use_case = providers.Factory(
        GetActorStatsToolUseCase,
        actor_stats_use_case=actor_stats_use_case,
        user_id=user_id,
    )

    get_sub_transactions_from_transaction_tool_use_case = providers.Factory(
        GetSubTransactionsFromTransactionToolUseCase,
        sub_transaction_serializer=sub_transaction_serializer,
        sub_transaction_factory=sub_transaction_factory,
        sub_transaction_repository=sub_transaction_repository,
        transaction_repository=transaction_repository,
        user_id=user_id,
    )

    get_user_general_stats_tool_use_case = providers.Factory(
        GetUserGeneralStatsToolUseCase,
        transaction_stats_use_case=transaction_stats_use_case,
        user_id=user_id,
    )

    get_transactions_tool_use_case = providers.Factory(
        GetTransactionsToolUseCase,
        transaction_repository=transaction_repository,
        transaction_serializer=transaction_serializer,
        transaction_factory=transaction_factory,
        user_id=user_id,
    )

    get_tools_for_ai_use_case = providers.Factory(
        GetToolsForAIUseCase,
        get_actors_tool_use_case=get_actors_tool_use_case,
        get_actor_detail_tool_use_case=get_actor_detail_tool_use_case,
        get_actor_stats_tool_use_case=get_actor_stats_tool_use_case,
        get_sub_transactions_from_transaction_tool_use_case=get_sub_transactions_from_transaction_tool_use_case,
        get_user_general_stats_tool_use_case=get_user_general_stats_tool_use_case,
        get_transactions_tool_use_case=get_transactions_tool_use_case,
    )
