from modules.ai.mcp.domains.sql_query import SqlQuery
from modules.ai.mcp.services.sql_validator import SqlValidatorService
from modules.ai.mcp.services.query_scoper import QueryScoperService


class SqlQueryFactory:
    def __init__(
        self,
        sql_validator: SqlValidatorService,
        query_scoper: QueryScoperService,
    ):
        self.sql_validator = sql_validator
        self.query_scoper = query_scoper

    def from_raw(self, raw: str, *, user_id: int) -> SqlQuery:
        cleaned = self.sql_validator.validate(raw)
        wrapped, params = self.query_scoper.scope(cleaned, user_id=user_id)
        return SqlQuery(raw=cleaned, wrapped=wrapped, params=params)
