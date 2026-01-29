from modules.ai.chat.domains import EmbeddingCallDomain
from modules.ai.models import EmbeddingCall


class EmbeddingCallFactory:
    def build_from_model(self, model: EmbeddingCall) -> EmbeddingCallDomain:
        return EmbeddingCallDomain(
            embedding=model.embedding,
            model=model.model,
            total_tokens=model.total_tokens,
            prompt_used_tokens=model.prompt_used_tokens,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )