from modules.transactions.domains.actor import ActorDomain
from modules.transactions.models import Actor


class ActorFactory:
    def build_from_model(self, model: Actor) -> ActorDomain:
        return ActorDomain(
            name=model.name,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            user_id=model.user_id,
        )

    def build(self, name: str, user_id: int) -> ActorDomain:
        return ActorDomain(name=name, user_id=user_id)
