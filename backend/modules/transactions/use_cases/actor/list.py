from modules.transactions.repositories.actor import ActorRepository
from modules.transactions.serializers.actor import ActorSerializer


class ListActorsUseCase:
    def __init__(self, actor_repository: ActorRepository, actor_serializer: ActorSerializer):
        self.actor_repository = actor_repository
        self.actor_serializer = actor_serializer

    def execute(self) -> list[dict]:
        actors = self.actor_repository.get_all()
        return [self.actor_serializer.serialize(actor) for actor in actors]
