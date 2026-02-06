from decimal import Decimal


class AICallDomain:
    def __init__(
        self,
        prompt: list[str] = None,
        response: dict = None,
        total_tokens: int = None,
        input_used_tokens: int = None,
        output_used_tokens: int = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        model: str = None,
        is_error: bool = False,
    ):
        self.prompt = prompt
        self.response = response
        self.total_tokens = total_tokens
        self.input_used_tokens = input_used_tokens
        self.output_used_tokens = output_used_tokens
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.model = model
        self.is_error = is_error

    def model_prices(self) -> dict[str, Decimal]:
        from modules.ai.types import LlmModels

        model_info = LlmModels.get_model(self.model)
        input_price = Decimal(str(model_info.input_cost_per_million_tokens)) * Decimal(str(self.input_used_tokens)) / Decimal('1000000')
        output_price = Decimal(str(model_info.output_cost_per_million_tokens)) * Decimal(str(self.output_used_tokens)) / Decimal('1000000')
        return {
            "input": input_price,
            "output": output_price,
            "total": input_price + output_price,
        }