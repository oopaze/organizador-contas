from typing import Any


LIST_TRANSACTIONS_DESCRIPTION = (
    "Lista as transações do usuário com as subtransações, usando os mesmos "
    "filtros do app. Aceita start/end (YYYY-MM-DD), month (YYYY-MM), "
    "transaction_type (incoming/outgoing), category, paid (true/false), "
    "search (trecho do identificador) e limit (padrão 50, máx 200)."
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
    "card_label."
)

UPDATE_TRANSACTION_DESCRIPTION = (
    "Atualiza campos da transação do usuário: transaction_identifier, "
    "total_amount, due_date, transaction_type, category, is_salary."
)

CREATE_SUB_TRANSACTION_DESCRIPTION = (
    "Adiciona uma subtransação a uma transação do usuário."
)

UPDATE_SUB_TRANSACTION_DESCRIPTION = (
    "Atualiza uma subtransação do usuário: description, amount, date, "
    "category, installment_info, actor, user_provided_description."
)

GET_PROJECTION_DESCRIPTION = (
    "Projeção mensal de 12 meses: salário garantido configurado menos o "
    "comprometimento das intenções de compra planejadas (parcelas), com a "
    "sobra de cada mês. Aceita start/end (YYYY-MM) e months."
)


def call_list_transactions(*, arguments: dict, use_case, user_id: int) -> dict:
    filters: dict[str, Any] = {"user_id": user_id}
    if arguments.get("start"):
        filters["due_date__gte"] = arguments["start"]
    if arguments.get("end"):
        filters["due_date__lte"] = arguments["end"]
    if arguments.get("month"):
        year, month = str(arguments["month"]).split("-")
        filters["due_date__year"] = int(year)
        filters["due_date__month"] = int(month)
    if arguments.get("transaction_type"):
        filters["transaction_type"] = arguments["transaction_type"]
    if arguments.get("category"):
        filters["category"] = arguments["category"]
    if arguments.get("paid") is not None:
        filters["paid_at__isnull"] = not bool(arguments["paid"])
    if arguments.get("search"):
        filters["transaction_identifier__icontains"] = arguments["search"]

    limit = min(int(arguments.get("limit") or 50), 200)
    transactions = use_case.execute(filters)
    return {"transactions": transactions[:limit], "count": min(len(transactions), limit)}


def call_get_transaction(*, arguments: dict, use_case, user_id: int) -> dict:
    return use_case.execute(arguments["transaction_id"], user_id)


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
            "category": arguments.get("category"),
            "actor_id": arguments.get("actor_id"),
            "card_label": arguments.get("card_label"),
            "card_id": arguments.get("card_id"),
        }
        if arguments.get("installments") is not None:
            data["installments"] = arguments["installments"]
        if arguments.get("is_paid") is not None:
            data["is_paid"] = arguments["is_paid"]
        return quick_add_use_case.execute(data, user_id)

    data = {
        "user_id": user_id,
        "transaction_identifier": arguments["transaction_identifier"],
        "total_amount": arguments["total_amount"],
        "due_date": arguments["due_date"],
        "transaction_type": arguments.get("transaction_type", "outgoing"),
        "category": arguments.get("category"),
        "is_salary": arguments.get("is_salary", False),
        "is_recurrent": arguments.get("is_recurrent", False),
        "recurrence_count": arguments.get("recurrence_count"),
        "paid_at": arguments.get("paid_at"),
    }
    return use_case.execute(data)


def call_update_transaction(*, arguments: dict, use_case, user_id: int) -> dict:
    fields = {key: value for key, value in arguments.items() if key != "transaction_id"}
    fields["user_id"] = user_id
    return use_case.execute(arguments["transaction_id"], fields)


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
    if arguments.get("actor_id"):
        data["actor"] = arguments["actor_id"]
    return use_case.execute(data, user_id)


def call_update_sub_transaction(*, arguments: dict, use_case, user_id: int) -> dict:
    fields = {
        key: value
        for key, value in arguments.items()
        if key != "sub_transaction_id"
    }
    return use_case.execute(arguments["sub_transaction_id"], fields, user_id)


def call_get_projection(*, arguments: dict, use_case, user_id: int) -> dict:
    return use_case.execute(
        user_id,
        start=arguments.get("start"),
        end=arguments.get("end"),
        months=int(arguments.get("months") or 12),
    )
