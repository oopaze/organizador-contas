LIST_CARDS_DESCRIPTION = (
    "Lista os cartões do usuário com id, nome, dia de vencimento e se está ativo. "
    "Use para resolver card_id antes de filtrar por cartão."
)

LIST_ACTORS_DESCRIPTION = (
    "Lista os atores (pessoas/entidades) do usuário com id e nome. "
    "Use para resolver actor_id antes de filtrar por ator."
)


def call_list_cards(*, arguments: dict, use_case, user_id: int) -> dict:
    cards = use_case.execute(user_id)
    return {
        "cards": [
            {"id": card["id"], "name": card["name"], "due_day": card["due_day"], "is_active": card["is_active"]}
            for card in cards
        ]
    }


def call_list_actors(*, arguments: dict, use_case, user_id: int) -> dict:
    actors = use_case.execute(user_id, without_sub_transactions=True)
    return {"actors": [{"id": actor["id"], "name": actor["name"]} for actor in actors]}
