from modules.transactions.domains.actor import ActorDomain
from modules.transactions.factories.actor import ActorFactory
from modules.transactions.models import Actor


class ActorRepository:
    def __init__(self, model: Actor, actor_factory: ActorFactory):
        self.model = model
        self.actor_factory = actor_factory
        self.queryset = self.model.objects.order_by("name")

    def get(self, actor_id: str, user_id: int) -> ActorDomain:
        actor_instance = self.queryset.get(id=actor_id, user_id=user_id)
        return self.actor_factory.build_from_model(actor_instance)

    def get_all(self, user_id: int, filters: dict = {}) -> list[ActorDomain]:
        actor_instances = self.queryset.filter(user_id=user_id, **filters)
        return [self.actor_factory.build_from_model(actor) for actor in actor_instances]

    def create(self, actor: ActorDomain) -> ActorDomain:
        actor_instance = self.model.objects.create(
            name=actor.name,
            user_id=actor.user_id,
        )
        return self.actor_factory.build_from_model(actor_instance)

    def update(self, actor: ActorDomain) -> ActorDomain:
        actor_instance = self.queryset.get(id=actor.id, user_id=actor.user_id)
        actor_instance.name = actor.name
        actor_instance.save()
        return self.actor_factory.build_from_model(actor_instance)

    def delete(self, actor_id: str, user_id: int):
        self.queryset.get(id=actor_id, user_id=user_id).delete()
