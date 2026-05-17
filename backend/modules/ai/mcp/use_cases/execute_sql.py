from typing import TYPE_CHECKING

from modules.ai.mcp.domains.query_result import QueryResult
from modules.ai.mcp.factories.sql_query import SqlQueryFactory

if TYPE_CHECKING:
    from modules.ai.mcp.gateways.readonly_postgres import ReadOnlyPostgresGateway


class ExecuteSqlUseCase:
    def __init__(
        self,
        sql_query_factory: SqlQueryFactory,
        readonly_postgres_gateway: "ReadOnlyPostgresGateway",
    ):
        self.sql_query_factory = sql_query_factory
        self.readonly_postgres_gateway = readonly_postgres_gateway

    def execute(self, raw_query: str, *, user_id: int) -> QueryResult:
        sql_query = self.sql_query_factory.from_raw(raw_query, user_id=user_id)
        return self.readonly_postgres_gateway.execute(sql_query)
