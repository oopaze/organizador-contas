import logging
from typing import Any, Optional

from modules.ai.mcp.exceptions import MCPError
from modules.ai.mcp.use_cases.describe_schema import DescribeSchemaUseCase


logger = logging.getLogger("modules.ai.mcp")


DESCRIBE_SCHEMA_DESCRIPTION = (
    "Retorna o schema das tabelas que você pode consultar. Sem parâmetro = "
    "lista todas. Com table = detalhe de uma só."
)


def call_describe_schema(
    *,
    table: Optional[str],
    use_case: DescribeSchemaUseCase,
) -> dict[str, Any]:
    logger.info("mcp.describe_schema table=%r", table)
    try:
        return use_case.execute(table=table)
    except MCPError as exc:
        return {"error": {"code": exc.code, "message": exc.message}}
