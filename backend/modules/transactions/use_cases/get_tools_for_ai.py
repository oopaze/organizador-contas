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

FALLBACK_MESSAGE = "Erro ao executar a função."


def fallback_in_case_of_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return {
                "result": result,
            }
        except Exception as e:
            return FALLBACK_MESSAGE
    return wrapper


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

    def execute(self) -> list[ToolListUnion]:
        return [
            fallback_in_case_of_error(self.get_actors_tool_use_case.get_actors),
            fallback_in_case_of_error(self.get_actor_detail_tool_use_case.get_actor_detail),
            fallback_in_case_of_error(self.get_actor_stats_tool_use_case.get_actor_stats),
            fallback_in_case_of_error(self.get_sub_transactions_from_transaction_tool_use_case.get_sub_transactions_from_transaction),
            fallback_in_case_of_error(self.get_user_general_stats_tool_use_case.get_user_general_stats),
            fallback_in_case_of_error(self.get_transactions_tool_use_case.get_transactions),
        ]
