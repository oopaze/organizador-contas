import functools

from google.genai.types import ToolListUnion

from modules.transactions.use_cases.tools import (
    GetActorsToolUseCase,
    GetActorDetailToolUseCase,
    GetActorStatsToolUseCase,
    GetSubTransactionsFromTransactionToolUseCase,
    GetUserGeneralStatsToolUseCase,
    GetTransactionsToolUseCase,
)


class ToolInterface:
    AI_CONFIG: dict

    def execute(self, **kwargs):
        raise NotImplementedError

    
class GetToolsForAIUseCase:
    def __init__(
        self,
        get_actors_tool_use_case: GetActorsToolUseCase,
        get_actor_detail_tool_use_case: GetActorDetailToolUseCase,
        get_actor_stats_tool_use_case: GetActorStatsToolUseCase,
        get_sub_transactions_from_transaction_tool_use_case: GetSubTransactionsFromTransactionToolUseCase,
        get_user_general_stats_tool_use_case: GetUserGeneralStatsToolUseCase,
        get_transactions_tool_use_case: GetTransactionsToolUseCase,
    ):
        self.get_actors_tool_use_case = get_actors_tool_use_case
        self.get_actor_detail_tool_use_case = get_actor_detail_tool_use_case
        self.get_actor_stats_tool_use_case = get_actor_stats_tool_use_case
        self.get_sub_transactions_from_transaction_tool_use_case = get_sub_transactions_from_transaction_tool_use_case
        self.get_user_general_stats_tool_use_case = get_user_general_stats_tool_use_case
        self.get_transactions_tool_use_case = get_transactions_tool_use_case

    def execute(self) -> list[dict]:
        return [
            self.get_actors_tool_use_case,
            self.get_actor_detail_tool_use_case,
            self.get_actor_stats_tool_use_case,
            self.get_sub_transactions_from_transaction_tool_use_case,
            self.get_user_general_stats_tool_use_case,
            self.get_transactions_tool_use_case,
        ]
