from modules.ai.types import LlmModels
from decimal import Decimal
from modules.base.constants import DOLAR_TO_BRL


class AICallDomain:
    def __init__(
        self,
        response: dict,
        prompt: list[str] = None,
        total_tokens: int = None,
        input_used_tokens: int = 0,
        output_used_tokens: int = 0,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        model: str = None,
        is_error: bool = False,
    ):
        self.response = response
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.prompt = prompt
        self.total_tokens = total_tokens
        self.input_used_tokens = input_used_tokens 
        self.output_used_tokens = output_used_tokens
        self.model = model
        self.input_cost, self.output_cost = self.calculate_costs()
        self.is_error = is_error

    def calculate_costs(self):
        if not self.model or self.input_used_tokens == 0 or self.output_used_tokens == 0:
            return Decimal(0), Decimal(0)

        model = LlmModels.get_model(self.model)

        input_cost = Decimal(self.input_used_tokens) * (Decimal(model.input_cost_per_million_tokens) / Decimal(1000000)) * DOLAR_TO_BRL
        output_cost =  Decimal(self.output_used_tokens) * (Decimal(model.output_cost_per_million_tokens) / Decimal(1000000)) * DOLAR_TO_BRL

        return input_cost, output_cost
