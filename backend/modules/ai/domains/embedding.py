from decimal import Decimal


class EmbeddingDomain:
    def __init__(
        self,
        embedding: list[float] = None,
        model: str = None,
        total_tokens: int = None,
        prompt_used_tokens: int = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
    ):
        self.embedding = embedding
        self.model = model
        self.total_tokens = total_tokens
        self.prompt_used_tokens = prompt_used_tokens
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.price = self.get_price()

    def set_embedding(self, embedding: list[float]):
        self.embedding = embedding

    def get_price(self) -> Decimal:
        from modules.ai.types import LlmModels

        model_info = LlmModels.get_model(self.model)
        return Decimal(str(model_info.input_cost_per_million_tokens)) * Decimal(str(self.prompt_used_tokens)) / Decimal('1000000')
