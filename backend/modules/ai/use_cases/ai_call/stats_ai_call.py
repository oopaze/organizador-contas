from decimal import Decimal

from modules.ai.factories.ai_call import AICallFactory
from modules.ai.repositories.ai_call import AICallRepository


class StatsAICallUseCase:
    def __init__(self, ai_call_repository: AICallRepository):
        self.ai_call_repository = ai_call_repository
        self.ai_call_factory = AICallFactory()

    def execute(self, user_id: int, filter_by_model: str = None, due_date_start: str = None, due_date_end: str = None) -> dict:
        ai_calls = self.ai_call_repository.get_all_by_user_id(user_id, filter_by_model, due_date_start, due_date_end)
        return self.calculate_stats(ai_calls)

    def calculate_stats(self, ai_calls: list) -> dict:
        total_tokens = 0
        total_input_tokens = 0
        total_output_tokens = 0
        total_errors = 0
        models_stats = {}
        amount_spent = {
            "input": Decimal('0'),
            "output": Decimal('0'),
            "total": Decimal('0'),
        }

        for ai_call in ai_calls:
            total_tokens += ai_call.total_tokens
            total_input_tokens += ai_call.input_used_tokens
            total_output_tokens += ai_call.output_used_tokens
            total_errors += 1 if ai_call.is_error else 0
            prices = ai_call.model_prices()
            amount_spent["input"] += prices["input"]
            amount_spent["output"] += prices["output"]
            amount_spent["total"] += prices["total"]

            if ai_call.model in models_stats:
                models_stats[ai_call.model]["count"] += 1
                models_stats[ai_call.model]["total_tokens"] += ai_call.total_tokens
                models_stats[ai_call.model]["total_input_tokens"] += ai_call.input_used_tokens
                models_stats[ai_call.model]["total_output_tokens"] += ai_call.output_used_tokens
                models_stats[ai_call.model]["total_spent"] += prices["total"]
            else:
                models_stats[ai_call.model] = { 
                    "count": 1,
                    "total_tokens": ai_call.total_tokens,
                    "total_input_tokens": ai_call.input_used_tokens,
                    "total_output_tokens": ai_call.output_used_tokens,
                    "total_spent": prices["total"],
                }

        return {
            "total_calls": len(ai_calls),
            "total_tokens": total_tokens,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_errors": total_errors,
            "models_stats": models_stats,
            "amount_spent": amount_spent,
        }
