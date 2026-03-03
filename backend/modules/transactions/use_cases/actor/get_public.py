from modules.transactions.repositories.actor import ActorRepository
from modules.transactions.serializers.actor import ActorSerializer
from modules.transactions.repositories.sub_transaction import SubTransactionRepository
from modules.transactions.serializers.sub_transaction import SubTransactionSerializer
from modules.transactions.services.share_token import ShareTokenService


class GetPublicActorUseCase:
    def __init__(
        self,
        actor_repository: ActorRepository,
        actor_serializer: ActorSerializer,
        sub_transaction_repository: SubTransactionRepository,
        sub_transaction_serializer: SubTransactionSerializer,
        share_token_service: ShareTokenService,
    ):
        self.actor_repository = actor_repository
        self.actor_serializer = actor_serializer
        self.sub_transaction_repository = sub_transaction_repository
        self.sub_transaction_serializer = sub_transaction_serializer
        self.share_token_service = share_token_service

    def execute(self, token: str, due_date: str = None) -> dict:
        actor_id = self.share_token_service.validate_token(token)
        if actor_id is None:
            raise ValueError("Invalid share token")

        actor = self.actor_repository.get_by_id(actor_id)
        sub_transactions = self.sub_transaction_repository.get_by_actor_id(actor.id, actor.user_id, due_date)
        actor.set_sub_transactions(sub_transactions)

        actor_data = self.actor_serializer.serialize(actor)
        actor_data["sub_transactions"] = [
            self.sub_transaction_serializer.serialize(sub_transaction, include_actor=False, include_transaction=True)
            for sub_transaction in sub_transactions
        ]
        return actor_data

