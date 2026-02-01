from modules.transactions.serializers import SubTransactionSerializer
from modules.transactions.factories import SubTransactionFactory
from modules.transactions.repositories import SubTransactionRepository, TransactionRepository


class GetSubTransactionsFromTransactionToolUseCase:
    AI_CONFIG = {
        "type": "function",
        "function": {
            "name": "get_sub_transactions_from_transaction",
            "description": "Get sub transactions from transaction. Use this tool when you need to understand better a specific transaction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "The transaction id",
                    },
                },
                "required": ["transaction_id"],
            },
        },
    }

    def __init__(
        self, 
        sub_transaction_serializer: SubTransactionSerializer, 
        sub_transaction_factory: SubTransactionFactory,
        sub_transaction_repository: SubTransactionRepository,
        transaction_repository: TransactionRepository,
        user_id: int = None,
    ):
        self.sub_transaction_serializer = sub_transaction_serializer
        self.sub_transaction_factory = sub_transaction_factory
        self.sub_transaction_repository = sub_transaction_repository
        self.transaction_repository = transaction_repository
        self.user_id = user_id

    def execute(self, transaction_id: int) -> str:
        return self.get_sub_transactions_from_transaction(transaction_id)

    def get_sub_transactions_from_transaction(self, transaction_id: int) -> str:
        """
        Get sub transactions from transaction. Use this tool when you need to understand better a specific transaction.

        Args:
            transaction_id: The transaction id.
        """
        print("GetSubTransactionsFromTransactionToolUseCase.execute", transaction_id)
        transaction = self.transaction_repository.get(transaction_id, self.user_id)
        transaction.set_sub_transactions(
            self.sub_transaction_repository.get_all_by_transaction_id(transaction_id, self.user_id)
        )
        sub_transactions_for_tool = self.sub_transaction_serializer.serialize_many_for_tool(transaction.sub_transactions)
        return f"Subtransações da transação (ID:{transaction_id}):\n{sub_transactions_for_tool}"
