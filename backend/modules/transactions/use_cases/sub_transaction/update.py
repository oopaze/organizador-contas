from modules.transactions.repositories import SubTransactionRepository, ActorRepository
from modules.transactions.serializers import SubTransactionSerializer
from modules.transactions.domains import SubTransactionDomain, ActorDomain


class UpdateSubTransactionUseCase:
    def __init__(
        self, 
        sub_transaction_repository: SubTransactionRepository, 
        sub_transaction_serializer: SubTransactionSerializer, 
        actor_repository: ActorRepository
    ):
        self.sub_transaction_repository = sub_transaction_repository
        self.sub_transaction_serializer = sub_transaction_serializer
        self.actor_repository = actor_repository

    def execute(self, id: int, data: dict, user_id: int) -> dict:
        sub_transaction = self.sub_transaction_repository.get(id, user_id)
        actor = self.actor_repository.get(data["actor"], user_id) if data.get("actor") else None

        if data.get("should_divide_for_actor", False) and actor:
            sub_transaction = self.give_part_to_actor(sub_transaction, data, actor)
            data.update({"actor": None, "actor_id": None, "amount": sub_transaction.amount})

        sub_transaction.update(data)
        
        updated_sub_transaction = self.sub_transaction_repository.update(sub_transaction)
        return self.sub_transaction_serializer.serialize(updated_sub_transaction)
    
    def give_part_to_actor(self, sub_transaction: SubTransactionDomain, data: dict, actor: ActorDomain) -> dict:
        current_user_provided_description = f"{sub_transaction.user_provided_description} - " if sub_transaction.user_provided_description else ""

        actor_sub_transaction = self.sub_transaction_repository.duplicate(
            sub_transaction.id, 
            {
                "amount": data.get("actor_amount", 0), 
                "actor_id": actor.id,
                "user_provided_description": current_user_provided_description + f'Parte de {actor.name} (#{sub_transaction.id})',
            }
        )

        sub_transaction.update({
            "actor_id": None,
            "amount": sub_transaction.amount - actor_sub_transaction.amount,
            "user_provided_description": current_user_provided_description,
        })
        return sub_transaction



