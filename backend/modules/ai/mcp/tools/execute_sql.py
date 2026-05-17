import logging
from typing import Any

from modules.ai.mcp.exceptions import MCPError
from modules.ai.mcp.use_cases.execute_sql import ExecuteSqlUseCase


logger = logging.getLogger("modules.ai.mcp")


EXECUTE_SQL_DESCRIPTION = (
    "Executa uma query SELECT read-only no banco do Poupix. Escopada "
    "automaticamente ao seu usuário; exclui registros soft-deleted. "
    "Limite de 1000 linhas e 5s de execução. Use os nomes de tabela do "
    "Django: transactions_transaction, transactions_subtransaction, "
    "transactions_actor, file_reader_file."
)


def call_execute_sql(
    *, query: str, use_case: ExecuteSqlUseCase, user_id: int
) -> dict[str, Any]:
    logger.info("mcp.execute_sql user_id=%s sql=%r", user_id, query[:500])
    try:
        result = use_case.execute(query, user_id=user_id)
        return result.to_dict()
    except MCPError as exc:
        logger.info("mcp.execute_sql error code=%s", exc.code)
        return {"error": {"code": exc.code, "message": exc.message}}
