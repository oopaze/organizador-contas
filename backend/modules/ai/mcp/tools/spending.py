from typing import Any

from modules.ai.mcp.categories import resolve_category
from modules.ai.mcp.dates import parse_month, validate_date
from modules.ai.mcp.exceptions import InvalidParamError


SUMMARIZE_SPENDING_DESCRIPTION = (
    "Soma gastos (ou entradas) com filtros e agrupamento no servidor — use para "
    "'quanto gastei com X'. due_* filtra o vencimento (fatura); purchase_* filtra "
    "a data da compra (subtransações; em transação sem subs vale o vencimento). "
    "Regra: fatura de cartão conta pelas subtransações (nunca pelo total), "
    "transação sem subs conta o total. group_by: none, category, card ou month. "
    "transaction_type padrão outgoing. Valores em BRL."
)

GROUP_BY_OPTIONS = ("none", "category", "card", "month")


def call_summarize_spending(*, arguments: dict, use_case, user_id: int) -> dict:
    filters: dict[str, Any] = {}
    if arguments.get("due_month"):
        year, month = parse_month(arguments["due_month"])
        filters["due_date__year"] = year
        filters["due_date__month"] = month
    if arguments.get("due_start"):
        filters["due_date__gte"] = validate_date(arguments["due_start"], "due_start")
    if arguments.get("due_end"):
        filters["due_date__lte"] = validate_date(arguments["due_end"], "due_end")
    if arguments.get("purchase_month"):
        parse_month(arguments["purchase_month"])
        filters["purchase_month"] = arguments["purchase_month"]
    if arguments.get("purchase_start"):
        filters["purchase_start"] = validate_date(arguments["purchase_start"], "purchase_start")
    if arguments.get("purchase_end"):
        filters["purchase_end"] = validate_date(arguments["purchase_end"], "purchase_end")
    category = resolve_category(arguments.get("category"))
    if category:
        filters["category"] = category
    if arguments.get("search"):
        filters["search"] = arguments["search"]
    filters["transaction_type"] = arguments.get("transaction_type") or "outgoing"

    group_by = arguments.get("group_by") or "none"
    if group_by not in GROUP_BY_OPTIONS:
        raise InvalidParamError(
            f"group_by inválido: {group_by!r}. Use um de: {', '.join(GROUP_BY_OPTIONS)}."
        )
    filters["group_by"] = group_by

    return use_case.execute(user_id, filters)
