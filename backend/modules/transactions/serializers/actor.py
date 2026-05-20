from modules.transactions.domains.actor import ActorDomain

ACTOR_FOR_TOOL_PROMPT = """
Ator {name}:
- id: {actor_id}
- Total gasto: {total_spent}
"""

ACTOR_DETAIL_FOR_TOOL_PROMPT = """
Ator {name}:
- id: {actor_id}
- Total gasto: {total_spent}
"""

class ActorSerializer:
    def serialize(self, actor: ActorDomain) -> dict:
        total_spent = actor.get_total_spent()
        total_spent_paid = actor.get_total_spent_paid()
        total_remaining = total_spent - total_spent_paid
        return {
            "id": actor.id,
            "name": actor.name,
            "created_at": actor.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": actor.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "total_spent": total_spent,
            "total_spent_paid": total_spent_paid,
            "total_remaining": total_remaining,
            "loan_total_lent": float(actor.get_loan_total_lent()),
            "loan_total_received": float(actor.get_loan_total_received()),
            "loan_total_outstanding": float(actor.get_loan_total_outstanding()),
            "active_loan_count": actor.get_active_loan_count(),
        }

    def serialize_many(self, actors: list[ActorDomain]) -> list[dict]:
        return [self.serialize(actor) for actor in actors]
    
    def serialize_for_tool(self, actor: ActorDomain) -> str:
        return ACTOR_FOR_TOOL_PROMPT.format(
            name=actor.name,
            actor_id=actor.id,
            total_spent=actor.total_spent,
        )
    
    def serialize_many_for_tool(self, actors: list[ActorDomain]) -> str:
        return "\n".join([self.serialize_for_tool(actor) for actor in actors])
