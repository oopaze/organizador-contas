from dependency_injector import containers, providers

from modules.ai.mcp.factories.enum_listing import EnumListingFactory
from modules.ai.mcp.factories.query_result import QueryResultFactory
from modules.ai.mcp.factories.sql_query import SqlQueryFactory
from modules.ai.mcp.factories.table_schema import TableSchemaFactory
from modules.ai.mcp.gateways.readonly_postgres import ReadOnlyPostgresGateway
from modules.ai.mcp.repositories.schema_introspection import (
    SchemaIntrospectionRepository,
)
from modules.ai.mcp.services.query_scoper import QueryScoperService
from modules.ai.mcp.services.sql_validator import SqlValidatorService
from modules.ai.mcp.use_cases.describe_schema import DescribeSchemaUseCase
from modules.ai.mcp.use_cases.execute_sql import ExecuteSqlUseCase
from modules.ai.mcp.use_cases.list_enums import ListEnumsUseCase


class MCPContainer(containers.DeclarativeContainer):
    # FACTORIES
    query_result_factory = providers.Singleton(QueryResultFactory)
    table_schema_factory = providers.Singleton(TableSchemaFactory)
    enum_listing_factory = providers.Singleton(EnumListingFactory)

    # SERVICES
    sql_validator = providers.Singleton(SqlValidatorService)
    query_scoper = providers.Singleton(QueryScoperService)

    sql_query_factory = providers.Singleton(
        SqlQueryFactory,
        sql_validator=sql_validator,
        query_scoper=query_scoper,
    )

    # GATEWAYS
    readonly_postgres_gateway = providers.Singleton(
        ReadOnlyPostgresGateway,
        query_result_factory=query_result_factory,
    )

    # REPOSITORIES
    schema_introspection_repository = providers.Singleton(
        SchemaIntrospectionRepository,
        table_schema_factory=table_schema_factory,
    )

    # USE CASES
    execute_sql_use_case = providers.Singleton(
        ExecuteSqlUseCase,
        sql_query_factory=sql_query_factory,
        readonly_postgres_gateway=readonly_postgres_gateway,
    )
    describe_schema_use_case = providers.Singleton(
        DescribeSchemaUseCase,
        schema_introspection_repository=schema_introspection_repository,
    )
    list_enums_use_case = providers.Singleton(
        ListEnumsUseCase,
        enum_listing_factory=enum_listing_factory,
    )
