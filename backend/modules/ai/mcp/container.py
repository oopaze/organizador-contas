from dependency_injector import containers, providers

from modules.ai.mcp.factories.enum_listing import EnumListingFactory
from modules.ai.mcp.use_cases.list_enums import ListEnumsUseCase
from modules.planning.container import PlanningContainer
from modules.transactions.container import TransactionsContainer
from modules.userdata.container import UserDataContainer


class MCPContainer(containers.DeclarativeContainer):
    # DEPENDENCIES (AI bits injected by the transports)
    ask_use_case = providers.Dependency()
    ai_call_repository = providers.Dependency()

    # FACTORIES
    enum_listing_factory = providers.Singleton(EnumListingFactory)

    # The domain use cases (transactions/subs) live in the transactions
    # module; MCP just reuses them so every tool is user-scoped and follows
    # the same business rules as the app.
    transactions_container = providers.Singleton(
        TransactionsContainer,
        ask_use_case=ask_use_case,
        ai_call_repository=ai_call_repository,
    )
    planning_container = providers.Singleton(
        PlanningContainer,
        ask_use_case=ask_use_case,
        ai_call_repository=ai_call_repository,
    )
    userdata_container = providers.Singleton(UserDataContainer)

    # USE CASES
    list_enums_use_case = providers.Singleton(
        ListEnumsUseCase,
        enum_listing_factory=enum_listing_factory,
    )
