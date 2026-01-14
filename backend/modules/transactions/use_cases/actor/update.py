from modules.transactions.repositories.actor import ActorRepository
from modules.transactions.serializers.actor import ActorSerializer


class UpdateActorUseCase:
    def __init__(self, actor_repository: ActorRepository, actor_serializer: ActorSerializer):
        self.actor_repository = actor_repository
        self.actor_serializer = actor_serializer

    def execute(self, actor_id: str, name: str) -> dict:
        actor = self.actor_repository.get(actor_id)
        actor.update(name)
        updated_actor = self.actor_repository.update(actor)
        return self.actor_serializer.serialize(updated_actor)
