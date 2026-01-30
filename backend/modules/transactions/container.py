from dependency_injector import containers, providers

from modules.transactions.factories import ActorFactory, TransactionFactory, SubTransactionFactory
from modules.transactions.factories.actor import ActorFactory
from modules.transactions.models import Actor, Transaction, SubTransaction
from modules.transactions.repositories import ActorRepository, TransactionRepository, SubTransactionRepository
from modules.transactions.serializers import ActorSerializer, TransactionSerializer, SubTransactionSerializer
from modules.transactions.factories import ActorFactory, TransactionFactory, SubTransactionFactory
from modules.transactions.use_cases.actor import (
    CreateActorUseCase,
    DeleteActorUseCase,
    GetActorUseCase,
    ListActorsUseCase,
    UpdateActorUseCase,
)
from modules.transactions.use_cases.transaction import (
    CreateTransactionUseCase,
    DeleteTransactionUseCase,
    GetTransactionUseCase,
    ListTransactionsUseCase,
    UpdateTransactionUseCase,
    TransactionStatsUseCase,
)
from modules.transactions.use_cases.sub_transaction import (
    CreateSubTransactionUseCase,
    DeleteSubTransactionUseCase,
    GetSubTransactionUseCase,
    ListSubTransactionsUseCase,
    UpdateSubTransactionUseCase,
)


class TransactionsContainer(containers.DeclarativeContainer):
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
    )

    update_transaction_use_case = providers.Factory(
        UpdateTransactionUseCase,
        transaction_repository=transaction_repository,
        transaction_serializer=transaction_serializer,
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
