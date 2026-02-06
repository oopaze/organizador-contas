from modules.ai.domains.embedding import EmbeddingDomain


class EmbeddingSerializer:
    def serialize(self, embedding: "EmbeddingDomain") -> dict:
        return {
            "id": embedding.id,
            "created_at": embedding.created_at,
            "updated_at": embedding.updated_at,
            "model": embedding.model,
            "total_tokens": embedding.total_tokens,
            "prompt_used_tokens": embedding.prompt_used_tokens,
            "price": embedding.price,
        }
