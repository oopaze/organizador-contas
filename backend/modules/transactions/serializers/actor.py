from modules.transactions.domains.actor import ActorDomain


class ActorSerializer:
    def serialize(self, actor: ActorDomain) -> dict:
        return {
            "id": actor.id,
            "name": actor.name,
            "created_at": actor.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": actor.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
