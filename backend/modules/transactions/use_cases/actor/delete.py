from modules.transactions.repositories.actor import ActorRepository


class DeleteActorUseCase:
    def __init__(self, actor_repository: ActorRepository):
        self.actor_repository = actor_repository

    def execute(self, actor_id: str):
        self.actor_repository.delete(actor_id)
