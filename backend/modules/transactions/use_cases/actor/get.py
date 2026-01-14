from modules.transactions.repositories.actor import ActorRepository
from modules.transactions.serializers.actor import ActorSerializer


class GetActorUseCase:
    def __init__(self, actor_repository: ActorRepository, actor_serializer: ActorSerializer):
        self.actor_repository = actor_repository
        self.actor_serializer = actor_serializer

    def execute(self, actor_id: str) -> dict:
        actor = self.actor_repository.get(actor_id)
        return self.actor_serializer.serialize(actor)
