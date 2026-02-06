from decimal import Decimal

from modules.ai.repositories.embedding import EmbeddingRepository


class StatsEmbeddingsUseCase:
    def __init__(self, embedding_repository: EmbeddingRepository):
        self.embedding_repository = embedding_repository

    def execute(self, user_id: int, due_date_start: str = None, due_date_end: str = None) -> dict:
        embeddings = self.embedding_repository.get_all_by_user_id(user_id, due_date_start, due_date_end)
        return self.calculate_stats(embeddings)

    def calculate_stats(self, embeddings: list) -> dict:
        total_tokens = 0
        total_prompt_tokens = 0
        total_errors = 0
        models_stats = {}
        amount_spent = Decimal('0')

        for embedding in embeddings:
            total_tokens += embedding.total_tokens
            total_prompt_tokens += embedding.prompt_used_tokens
            amount_spent += embedding.price

            if embedding.model in models_stats:
                models_stats[embedding.model]["count"] += 1
                models_stats[embedding.model]["total_tokens"] += embedding.total_tokens
                models_stats[embedding.model]["total_prompt_tokens"] += embedding.prompt_used_tokens
            else:
                models_stats[embedding.model] = { 
                    "count": 1,
                    "total_tokens": embedding.total_tokens,
                    "total_prompt_tokens": embedding.prompt_used_tokens,
                }
        
        return {
            "total_embeddings": len(embeddings),
            "total_tokens": total_tokens,
            "total_prompt_tokens": total_prompt_tokens,
            "total_errors": total_errors,
            "models_stats": models_stats,
            "amount_spent": amount_spent,
        }
