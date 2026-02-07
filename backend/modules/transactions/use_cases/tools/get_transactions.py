import logging

from modules.transactions.serializers import TransactionSerializer
from modules.transactions.factories import TransactionFactory
from modules.transactions.repositories import TransactionRepository

logging = logging.getLogger(__name__)


class GetTransactionsToolUseCase:
    AI_CONFIG = {
        "type": "function",
        "function": {
            "name": "get_transactions",
            "description": "Get transactions. Use this tool when knowing the transactions is relevant to answer the question in a specific period.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_type": {
                        "type": "string",
                        "description": "The transaction type",
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
                "required": ["due_date_start", "due_date_end"],
            },
        },
    }

    def __init__(
        self, 
        transaction_repository: TransactionRepository, 
        transaction_serializer: TransactionSerializer, 
        transaction_factory: TransactionFactory,
        user_id: int = None,
    ):
        self.transaction_repository = transaction_repository
        self.transaction_serializer = transaction_serializer
        self.transaction_factory = transaction_factory
        self.user_id = user_id

    def execute(self, transaction_type: str = None, due_date_start: str = None, due_date_end: str = None) -> str:
        return self.get_transactions(transaction_type, due_date_start, due_date_end)

    def get_transactions(self, transaction_type: str = None, due_date_start: str = None, due_date_end: str = None) -> str:
        """
        Get transactions. Use this tool when knowing the transactions is relevant to answer the question in a specific period.

        Args:
            transaction_type (Optional[str]): The transaction type (incoming|outgoing).
            due_date_start: The due date start in YYYY-MM-DD format.
            due_date_end: The due date end in YYYY-MM-DD format.
        """
        logging.info(f"GetTransactionsToolUseCase.execute {transaction_type=}, {due_date_start=}, {due_date_end=}")
        filters = {"user_id": self.user_id, "due_date__gte": due_date_start, "due_date__lte": due_date_end}
        if transaction_type:
            filters["transaction_type"] = transaction_type

        transactions = self.transaction_repository.filter(filters)
        return self.transaction_serializer.serialize_many_for_tool(transactions)
