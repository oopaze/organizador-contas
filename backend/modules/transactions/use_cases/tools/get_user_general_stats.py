from modules.transactions.use_cases.transaction.stats import TransactionStatsUseCase


TRANSACTION_STATS_FOR_TOOL_PROMPT = """
Estatísticas das transações no período:

- Total de entradas: {incoming_total}
- Total de saídas: {outgoing_total}
- Saldo: {balance}
- Total de saídas de atores: {outgoing_from_actors}
"""


class GetUserGeneralStatsToolUseCase:
    AI_CONFIG = {
        "type": "function",
        "function": {
            "name": "get_user_general_stats",
            "description": "Get user general stats. Use this tool to get a resume of the user's transactions in a specific period.",
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
        transaction_stats_use_case: TransactionStatsUseCase,
        user_id: int = None,
    ):
        self.transaction_stats_use_case = transaction_stats_use_case
        self.user_id = user_id

    def execute(self, due_date_start: str, due_date_end: str) -> str:
        return self.get_user_general_stats(due_date_start, due_date_end)

    def get_user_general_stats(self, due_date_start: str, due_date_end: str) -> str:
        """
        Get user general stats. Use this tool to get a resume of the user's transactions in a specific period.

        Args:
            due_date_start: The due date start in YYYY-MM-DD format.
            due_date_end: The due date end in YYYY-MM-DD format.
        """
        print("GetUserGeneralStatsToolUseCase.execute", due_date_start, due_date_end)
        stats = self.transaction_stats_use_case.execute(self.user_id, due_date_start=due_date_start, due_date_end=due_date_end)
        return TRANSACTION_STATS_FOR_TOOL_PROMPT.format(**stats)
