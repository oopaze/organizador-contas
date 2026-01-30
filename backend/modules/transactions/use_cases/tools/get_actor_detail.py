from modules.transactions.repositories import ActorRepository, SubTransactionRepository
from modules.transactions.serializers import ActorSerializer, SubTransactionSerializer

SUB_TRANSACTIONS_FOR_TOOL_PROMPT = """
{actor}

Subtransações:
{sub_transactions}
"""


class GetActorDetailToolUseCase:
    AI_CONFIG = {
        "name": "get_actor_detail",
        "description": "Get actor detail. Use this tool to get a resume of the actor spent in a specific period.",
        "parameters": {
            "type": "object",
            "properties": {
                "actor_id": {
                    "type": "string",
                    "description": "The actor id",
                },
                "due_date_start": {
                    "type": "string",
                    "description": "The due date start in YYYY-MM-DD format",
                },
                "due_date_end": {
                    "type": "string",
                    "description": "The due date end in YYYY-MM-DD format",
                },
            },
            "required": ["actor_id", "due_date_start", "due_date_end"],
        },
    }

    def __init__(
        self, 
        actor_repository: ActorRepository, 
        actor_serializer: ActorSerializer, 
        sub_transaction_repository: SubTransactionRepository, 
        sub_transaction_serializer: SubTransactionSerializer,
        user_id: int = None,
    ):
        self.actor_repository = actor_repository
        self.actor_serializer = actor_serializer
        self.sub_transaction_serializer = sub_transaction_serializer
        self.sub_transaction_repository = sub_transaction_repository
        self.user_id = user_id

    def execute(self, actor_id: str, due_date_start: str, due_date_end: str) -> str:
        return self.get_actor_detail(actor_id, due_date_start, due_date_end)

    def get_actor_detail(self, actor_id: str, due_date_start: str, due_date_end: str) -> str:
        """
        Get actor detail. Use this tool to get a resume of the actor spent in a specific period.

        Args:
            actor_id: The actor id.
            due_date_start: The due date start in YYYY-MM-DD format.
            due_date_end: The due date end in YYYY-MM-DD format.
        """
        print("GetActorDetailToolUseCase.execute", actor_id, due_date_start, due_date_end)
        actor = self.actor_repository.get(actor_id, self.user_id)
        filters = {
            "transaction__due_date__gte": due_date_start, 
            "transaction__due_date__lte": due_date_end, 
            "transaction__user_id": self.user_id
        }
        sub_transactions = self.sub_transaction_repository.filter_by_actor_id(actor_id, filters)
        actor.set_sub_transactions(sub_transactions)
        return SUB_TRANSACTIONS_FOR_TOOL_PROMPT.format(
            actor=self.actor_serializer.serialize_for_tool(actor),
            sub_transactions=self.sub_transaction_serializer.serialize_many_for_tool(actor.sub_transactions),
        )
