from typing import Any

from modules.ai.mcp.categories import resolve_category, with_category_slug
from modules.ai.mcp.dates import parse_month, validate_date


LIST_SUB_TRANSACTIONS_DESCRIPTION = (
    "Lista compras (subtransações) de forma plana e filtrável. purchase_month "
    "(YYYY-MM) e purchase_start/purchase_end (YYYY-MM-DD) filtram a data da "
    "compra; due_month e due_start/due_end filtram o vencimento da fatura pai. "
    "category aceita slug ou label; search casa a descrição; transaction_id e "
    "actor_id restringem à fatura/ator. limit padrão 100, máx 200. Valores em BRL."
)


def call_list_sub_transactions(*, arguments: dict, use_case, user_id: int) -> dict:
    filters: dict[str, Any] = {}
    if arguments.get("purchase_month"):
        year, month = parse_month(arguments["purchase_month"])
        filters["date__year"] = year
        filters["date__month"] = month
    if arguments.get("purchase_start"):
        filters["date__gte"] = validate_date(arguments["purchase_start"], "purchase_start")
    if arguments.get("purchase_end"):
        filters["date__lte"] = validate_date(arguments["purchase_end"], "purchase_end")
    if arguments.get("due_month"):
        year, month = parse_month(arguments["due_month"])
        filters["transaction__due_date__year"] = year
        filters["transaction__due_date__month"] = month
    if arguments.get("due_start"):
        filters["transaction__due_date__gte"] = validate_date(arguments["due_start"], "due_start")
    if arguments.get("due_end"):
        filters["transaction__due_date__lte"] = validate_date(arguments["due_end"], "due_end")
    category = resolve_category(arguments.get("category"))
    if category:
        filters["category"] = category
    if arguments.get("search"):
        filters["description__icontains"] = arguments["search"]
    if arguments.get("transaction_id"):
        filters["transaction_id"] = arguments["transaction_id"]
    if arguments.get("actor_id"):
        filters["actor_id"] = arguments["actor_id"]

    limit = min(int(arguments.get("limit") or 100), 200)
    sub_transactions = use_case.execute(user_id, filters=filters)[:limit]
    sub_transactions = [with_category_slug(sub_transaction) for sub_transaction in sub_transactions]
    return {"sub_transactions": sub_transactions, "count": len(sub_transactions)}
