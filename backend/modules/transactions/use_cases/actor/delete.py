from modules.transactions.repositories.actor import ActorRepository


class DeleteActorUseCase:
    def __init__(self, actor_repository: ActorRepository, loan_repository=None):
        self.actor_repository = actor_repository
        self.loan_repository = loan_repository

    def execute(self, actor_id: int, user_id: int) -> None:
        if self.loan_repository and self.loan_repository.has_active_for_actor(actor_id, user_id):
            raise ValueError("Actor possui empréstimos ativos e não pode ser removido")
        self.actor_repository.delete(actor_id, user_id)
