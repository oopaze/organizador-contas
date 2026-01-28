from modules.transactions.repositories.actor import ActorRepository
from modules.transactions.serializers.actor import ActorSerializer
from modules.transactions.repositories.sub_transaction import SubTransactionRepository
from modules.transactions.serializers.sub_transaction import SubTransactionSerializer


class GetActorUseCase:
    def __init__(
        self, 
        actor_repository: ActorRepository, 
        actor_serializer: ActorSerializer, 
        sub_transaction_repository: SubTransactionRepository, 
        sub_transaction_serializer: SubTransactionSerializer
    ):
        self.actor_repository = actor_repository
        self.actor_serializer = actor_serializer
        self.sub_transaction_repository = sub_transaction_repository
        self.sub_transaction_serializer = sub_transaction_serializer

    def execute(self, actor_id: str, user_id: int, due_date: str = None) -> dict:
        actor = self.actor_repository.get(actor_id, user_id)
        sub_transactions = self.sub_transaction_repository.get_by_actor_id(actor_id, user_id, due_date)
        actor.set_sub_transactions(sub_transactions)
        
        actor_data = self.actor_serializer.serialize(actor)
        actor_data["sub_transactions"] = [
            self.sub_transaction_serializer.serialize(sub_transaction, include_actor=False) 
            for sub_transaction in sub_transactions
        ]
        return actor_data
