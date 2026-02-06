from decimal import Decimal
from modules.base.constants import DOLAR_TO_BRL
from modules.ai.types import LlmModels


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
        related_to: str = None,
        file_url: str = None,
        conversation_title: str = None,
        user_message_content: str = None,
        ai_message_content: str = None,
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
        self.related_to = related_to
        self.file_url = file_url
        self.conversation_title = conversation_title
        self.user_message_content = user_message_content
        self.ai_message_content = ai_message_content

    def model_prices(self) -> dict[str, Decimal]:
        model_info = LlmModels.get_model(self.model)
        input_price = Decimal(str(model_info.input_cost_per_million_tokens)) * Decimal(str(self.input_used_tokens)) / Decimal('1000000')
        output_price = Decimal(str(model_info.output_cost_per_million_tokens)) * Decimal(str(self.output_used_tokens)) / Decimal('1000000')
        return {
            "input": input_price * DOLAR_TO_BRL,
            "output": output_price * DOLAR_TO_BRL,
            "total": (input_price + output_price) * DOLAR_TO_BRL,
        }