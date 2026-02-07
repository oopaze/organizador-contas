import logging

from modules.transactions.repositories import ActorRepository, SubTransactionRepository
from modules.transactions.serializers import ActorSerializer

logging = logging.getLogger(__name__)


class GetActorsToolUseCase:
    AI_CONFIG = {
        "type": "function",
        "function": {
            "name": "get_actors",
            "description": "Get actors. Use this tool when you need to list the actors in a specific period.",
            "parameters": {
                "type": "object",
                "properties": {
                    "due_date_start": {
                        "type": "string",
                        "description": "The due date start in YYYY-MM-DD format",
                    },
                    "due_date_end": {
                        "type": "string",
                        "description": "The due date end in YYYY-MM-DD format",
                    },
                },
                "required": ["due_date_start", "due_date_end"],
            },
        },
    }

    def __init__(
        self, 
        actor_repository: ActorRepository, 
        actor_serializer: ActorSerializer, 
        sub_transaction_repository: SubTransactionRepository,
        user_id: int = None,
    ):
        self.actor_repository = actor_repository
        self.actor_serializer = actor_serializer
        self.sub_transaction_repository = sub_transaction_repository
        self.user_id = user_id

    def execute(self, due_date_start: str, due_date_end: str) -> str:
        return self.get_actors(due_date_start, due_date_end)

    def get_actors(self, due_date_start: str, due_date_end: str) -> str:
        """
        Get actors. Use this tool when you need to list the actors in a specific period.

        Args:
            due_date_start: The due date start in YYYY-MM-DD format.
            due_date_end: The due date end in YYYY-MM-DD format.
        """
        logging.info(f"GetActorsToolUseCase.execute {due_date_start=}, {due_date_end=}")
        actors = self.actor_repository.get_all(self.user_id)
        filters = {
            "transaction__due_date__gte": due_date_start, 
            "transaction__due_date__lte": due_date_end, 
            "transaction__user_id": self.user_id
        }
        sub_transactions = self.sub_transaction_repository.filter_by_actor_ids([actor.id for actor in actors], filters)
        actors_with_sub_transactions = []
        for actor in actors:
            actor_sub_transactions = [sub_transaction for sub_transaction in sub_transactions if sub_transaction.actor.id == actor.id]
            if actor_sub_transactions:
                actor.set_sub_transactions(actor_sub_transactions)
                actors_with_sub_transactions.append(actor)
        return self.actor_serializer.serialize_many_for_tool(actors_with_sub_transactions)
