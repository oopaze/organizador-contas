from modules.transactions.domains.actor import ActorDomain
from modules.transactions.models import Actor


class ActorFactory:
    def build_from_model(self, model: Actor) -> ActorDomain:
        return ActorDomain(
            name=model.name,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def build(self, name: str) -> ActorDomain:
        return ActorDomain(name=name)
