from modules.transactions.factories.actor import ActorFactory
from modules.transactions.repositories.actor import ActorRepository
from modules.transactions.serializers.actor import ActorSerializer


class CreateActorUseCase:
    def __init__(self, actor_repository: ActorRepository, actor_serializer: ActorSerializer, actor_factory: ActorFactory):
        self.actor_repository = actor_repository
        self.actor_serializer = actor_serializer
        self.actor_factory = actor_factory

    def execute(self, name: str, user_id: int) -> dict:
        actor = self.actor_repository.create(self.actor_factory.build(name, user_id))
        return self.actor_serializer.serialize(actor)
