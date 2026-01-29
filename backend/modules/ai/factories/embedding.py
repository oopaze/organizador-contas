from openai.types import CreateEmbeddingResponse

from modules.ai.domains.embedding import EmbeddingDomain
from modules.ai.models import EmbeddingCall


class EmbeddingFactory:
    def build_from_model(self, model: EmbeddingCall) -> EmbeddingDomain:
        return EmbeddingDomain(
            embedding=model.embedding,
            model=model.model,
            total_tokens=model.total_tokens,
            prompt_used_tokens=model.prompt_used_tokens,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def build_from_embedding_model_response(self, embedding_model_response: CreateEmbeddingResponse, model: str) -> EmbeddingDomain:
        return EmbeddingDomain(
            embedding=embedding_model_response.data[0].embedding,
            model=model,
            total_tokens=embedding_model_response.usage.total_tokens,
            prompt_used_tokens=embedding_model_response.usage.prompt_tokens,
        )
