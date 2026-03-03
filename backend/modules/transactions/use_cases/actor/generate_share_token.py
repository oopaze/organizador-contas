from modules.transactions.repositories.actor import ActorRepository
from modules.transactions.services.share_token import ShareTokenService


class GenerateActorShareTokenUseCase:
    def __init__(
        self, 
        actor_repository: ActorRepository, 
        share_token_service: ShareTokenService,
    ):
        self.actor_repository = actor_repository
        self.share_token_service = share_token_service

    def execute(self, actor_id: int, user_id: int) -> str:
        # Verify the actor exists and belongs to the user
        actor = self.actor_repository.get(actor_id, user_id)
        return self.share_token_service.generate_token(actor.id)

