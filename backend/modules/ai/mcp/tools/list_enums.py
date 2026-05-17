import logging
from typing import Any

from modules.ai.mcp.use_cases.list_enums import ListEnumsUseCase


logger = logging.getLogger("modules.ai.mcp")


LIST_ENUMS_DESCRIPTION = (
    "Retorna valores válidos para colunas enum (category, transaction_type). "
    "Use antes de filtrar por category para garantir o slug correto."
)


def call_list_enums(*, use_case: ListEnumsUseCase) -> dict[str, Any]:
    logger.info("mcp.list_enums")
    return use_case.execute()
