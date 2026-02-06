from modules.ai.repositories.embedding import EmbeddingRepository
from modules.ai.serializers.embedding import EmbeddingSerializer

class ListEmbeddingsUseCase:
    def __init__(self, embedding_repository: EmbeddingRepository, embedding_serializer: EmbeddingSerializer):
        self.embedding_repository = embedding_repository
        self.embedding_serializer = embedding_serializer

    def execute(self, user_id: int, due_date_start: str = None, due_date_end: str = None) -> list[dict]:
        embeddings = self.embedding_repository.get_all_by_user_id(user_id, due_date_start, due_date_end)
        return [self.embedding_serializer.serialize(embedding) for embedding in embeddings]
