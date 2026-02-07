import logging

from modules.transactions.use_cases.actor.stats import ActorStatsUseCase

logging = logging.getLogger(__name__)


ACTOR_STATS_FOR_TOOL_PROMPT = """
Estatísticas dos atores no perido:

- Total gasto: {total_spent}
- Maior gastador: {biggest_spender} ({biggest_spender_amount})
- Menor gastador: {smallest_spender} ({smallest_spender_amount})
- Média gasta por ator: {average_spent}
- Atores ativos: {active_actors}
"""


class GetActorStatsToolUseCase:
    AI_CONFIG = {
        "type": "function",
        "function": {
            "name": "get_actor_stats",
            "description": "Get actor stats. Use this tool to get a resume of the actors spent in a specific period.",
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
        }
    }

    def __init__(self, actor_stats_use_case: ActorStatsUseCase, user_id: int = None):
        self.actor_stats_use_case = actor_stats_use_case
        self.user_id = user_id

    def execute(self, due_date_start: str, due_date_end: str) -> str:
        return self.get_actor_stats(due_date_start, due_date_end)

    def get_actor_stats(self, due_date_start: str, due_date_end: str) -> str:
        """
        Get actor stats. Use this tool to get a resume of the actors spent in a specific period.

        Args:
            due_date_start: The due date start in YYYY-MM-DD format.
            due_date_end: The due date end in YYYY-MM-DD format.
        """
        logging.info(f"GetActorStatsToolUseCase.execute {due_date_start=}, {due_date_end=}")
        stats = self.actor_stats_use_case.execute(self.user_id, due_date_start, due_date_end)
        return ACTOR_STATS_FOR_TOOL_PROMPT.format(**stats)
