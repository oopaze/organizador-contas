from typing import Any

from modules.ai.mcp.categories import enrich_transaction, resolve_category, with_category_slug
from modules.ai.mcp.dates import parse_month, validate_date


LIST_TRANSACTIONS_DESCRIPTION = (
    "Lista transações (faturas/documentos) do usuário. due_month (YYYY-MM) e "
    "due_start/due_end (YYYY-MM-DD) filtram o vencimento. search casa o "
    "identificador ou a descrição de subtransações. category aceita slug ou "
    "label (use list_enums). include_subtransactions=true devolve as compras de "
    "cada transação. limit padrão 50, máx 200. Valores em BRL."
)

GET_TRANSACTION_DESCRIPTION = (
    "Retorna uma transação do usuário pelo id, incluindo as subtransações."
)

CREATE_TRANSACTION_DESCRIPTION = (
    "Cria uma transação para o usuário. Com payment_method cash "
    "(dinheiro/débito/pix) ou credit (cartão, exige card_label) usa o "
    "lançamento rápido; cartão entra na fatura em aberto e aceita "
    "installments. Sem payment_method cria direto (aceita is_salary e "
    "is_recurrent com recurrence_count). paid_at/is_paid opcionais. "
    "cartão pode ser referenciado por card_id (cadastrado em /cards/) ou "
    "card_label. category aceita slug ou label (use list_enums). Valores em BRL."
)

UPDATE_TRANSACTION_DESCRIPTION = (
    "Atualiza campos da transação do usuário: transaction_identifier, "
    "total_amount, due_date, transaction_type, category, is_salary. "
    "category aceita slug ou label (use list_enums). Valores em BRL."
)

CREATE_SUB_TRANSACTION_DESCRIPTION = (
    "Adiciona uma subtransação a uma transação do usuário. category aceita "
    "slug ou label (use list_enums). Valores em BRL."
)

UPDATE_SUB_TRANSACTION_DESCRIPTION = (
    "Atualiza uma subtransação do usuário: description, amount, date, "
    "category, installment_info, actor, user_provided_description. "
    "category aceita slug ou label (use list_enums). Valores em BRL."
)

GET_PROJECTION_DESCRIPTION = (
    "Projeção mensal de 12 meses: salário garantido configurado menos o "
    "comprometimento das intenções de compra planejadas (parcelas), com a "
    "sobra de cada mês. Aceita start/end (YYYY-MM) e months."
)

SET_GOALS_DESCRIPTION = (
    "Atualiza as metas financeiras do usuǭrio em percentual da renda: "
    "spending_goal_percent (teto de gasto), savings_goal_percent (quanto "
    "guardar) e essentials_goal_percent (teto de gastos essenciais). "
    "Valores de 0 a 100. Retorna o perfil atualizado com as metas salvas."
)

GOAL_FIELDS = (
    "spending_goal_percent",
    "savings_goal_percent",
    "essentials_goal_percent",
)


def call_list_transactions(*, arguments: dict, use_case, user_id: int) -> dict:
    filters: dict[str, Any] = {"user_id": user_id}
    if arguments.get("due_month"):
        year, month = parse_month(arguments["due_month"])
        filters["due_date__year"] = year
        filters["due_date__month"] = month
    if arguments.get("due_start"):
        filters["due_date__gte"] = validate_date(arguments["due_start"], "due_start")
    if arguments.get("due_end"):
        filters["due_date__lte"] = validate_date(arguments["due_end"], "due_end")
    if arguments.get("transaction_type"):
        filters["transaction_type"] = arguments["transaction_type"]
    category = resolve_category(arguments.get("category"))
    if category:
        filters["category"] = category
    if arguments.get("paid") is not None:
        filters["paid_at__isnull"] = not bool(arguments["paid"])
    if arguments.get("search"):
        filters["search"] = arguments["search"]

    limit = min(int(arguments.get("limit") or 50), 200)
    transactions = use_case.execute(
        filters,
        include_subtransactions=bool(arguments.get("include_subtransactions")),
    )
    transactions = [enrich_transaction(transaction) for transaction in transactions[:limit]]
    return {"transactions": transactions, "count": len(transactions)}


def call_get_transaction(*, arguments: dict, use_case, user_id: int) -> dict:
    return enrich_transaction(use_case.execute(arguments["transaction_id"], user_id))


def call_create_transaction(
    *, arguments: dict, use_case, quick_add_use_case, user_id: int
) -> dict:
    if arguments.get("payment_method"):
        data: dict[str, Any] = {
            "direction": arguments.get("transaction_type", "outgoing"),
            "payment_method": arguments["payment_method"],
            "amount": arguments["total_amount"],
            "description": arguments["transaction_identifier"],
            "date": arguments["due_date"],
            "category": resolve_category(arguments.get("category")),
            "actor_id": arguments.get("actor_id"),
            "card_label": arguments.get("card_label"),
            "card_id": arguments.get("card_id"),
        }
        if arguments.get("installments") is not None:
            data["installments"] = arguments["installments"]
        if arguments.get("is_paid") is not None:
            data["is_paid"] = arguments["is_paid"]
        return enrich_transaction(quick_add_use_case.execute(data, user_id))

    data = {
        "user_id": user_id,
        "transaction_identifier": arguments["transaction_identifier"],
        "total_amount": arguments["total_amount"],
        "due_date": arguments["due_date"],
        "transaction_type": arguments.get("transaction_type", "outgoing"),
        "category": resolve_category(arguments.get("category")),
        "is_salary": arguments.get("is_salary", False),
        "is_recurrent": arguments.get("is_recurrent", False),
        "recurrence_count": arguments.get("recurrence_count"),
        "paid_at": arguments.get("paid_at"),
    }
    return enrich_transaction(use_case.execute(data))


def call_update_transaction(*, arguments: dict, use_case, user_id: int) -> dict:
    fields = {key: value for key, value in arguments.items() if key != "transaction_id"}
    fields["user_id"] = user_id
    if "category" in fields:
        fields["category"] = resolve_category(fields["category"])
    return enrich_transaction(use_case.execute(arguments["transaction_id"], fields))


def call_create_sub_transaction(*, arguments: dict, use_case, user_id: int) -> dict:
    data: dict[str, Any] = {
        "transaction_id": arguments["transaction_id"],
        "description": arguments["description"],
        "amount": arguments["amount"],
        "date": arguments.get("date"),
        "category": arguments.get("category"),
        "installment_info": arguments.get("installment_info"),
        "paid_at": arguments.get("paid_at"),
    }
    if "category" in data:
        data["category"] = resolve_category(data["category"])
    if arguments.get("actor_id"):
        data["actor"] = arguments["actor_id"]
    return with_category_slug(use_case.execute(data, user_id))


def call_update_sub_transaction(*, arguments: dict, use_case, user_id: int) -> dict:
    fields = {
        key: value
        for key, value in arguments.items()
        if key != "sub_transaction_id"
    }
    if "category" in fields:
        fields["category"] = resolve_category(fields["category"])
    return with_category_slug(use_case.execute(arguments["sub_transaction_id"], fields, user_id))


def call_get_projection(*, arguments: dict, use_case, user_id: int) -> dict:
    return use_case.execute(
        user_id,
        start=arguments.get("start"),
        end=arguments.get("end"),
        months=int(arguments.get("months") or 12),
    )


def call_set_goals(*, arguments: dict, update_profile_use_case, profile_repository, user_id: int) -> dict:
    profile = profile_repository.get_by_user_id(user_id)
    data = {
        field: str(arguments[field])
        for field in GOAL_FIELDS
        if arguments.get(field) is not None
    }
    return update_profile_use_case.execute(profile.id, data)
