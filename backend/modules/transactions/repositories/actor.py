from modules.transactions.domains.actor import ActorDomain
from modules.transactions.factories.actor import ActorFactory
from modules.transactions.models import Actor


class ActorRepository:
    def __init__(self, model: Actor, actor_factory: ActorFactory):
        self.model = model
        self.actor_factory = actor_factory

    def get(self, actor_id: str) -> ActorDomain:
        actor_instance = self.model.objects.get(id=actor_id)
        return self.actor_factory.build_from_model(actor_instance)
    
    def get_all(self) -> list[ActorDomain]:
        actor_instances = self.model.objects.all()
        return [self.actor_factory.build_from_model(actor) for actor in actor_instances]
    
    def create(self, actor: ActorDomain) -> ActorDomain:
        actor_instance = self.model.objects.create(name=actor.name)
        return self.actor_factory.build_from_model(actor_instance)

    def update(self, actor: ActorDomain) -> ActorDomain:
        actor_instance = self.model.objects.get(id=actor.id)
        actor_instance.name = actor.name
        actor_instance.save()
        return self.actor_factory.build_from_model(actor_instance)
    
    def delete(self, actor_id: str):
        self.model.objects.get(id=actor_id).delete()
