from modules.transactions.domains.actor import ActorDomain

ACTOR_FOR_TOOL_PROMPT = """
Ator {name} (#{actor_id}):
- Total gasto: {total_spent}
"""

ACTOR_DETAIL_FOR_TOOL_PROMPT = """
Ator {name} (#{actor_id}):
- Total gasto: {total_spent}
"""

class ActorSerializer:
    def serialize(self, actor: ActorDomain) -> dict:
        return {
            "id": actor.id,
            "name": actor.name,
            "created_at": actor.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": actor.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "total_spent": actor.total_spent,
        }
    
    def serialize_for_tool(self, actor: ActorDomain) -> str:
        return ACTOR_FOR_TOOL_PROMPT.format(
            name=actor.name,
            actor_id=actor.id,
            total_spent=actor.total_spent,
        )
    
    def serialize_many_for_tool(self, actors: list[ActorDomain]) -> str:
        return "\n".join([self.serialize_for_tool(actor) for actor in actors])
