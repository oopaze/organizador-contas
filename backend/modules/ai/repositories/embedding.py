from modules.ai.domains.embedding import EmbeddingDomain
from modules.ai.factories.embedding import EmbeddingFactory
from modules.ai.models import EmbeddingCall


class EmbeddingRepository:
    def __init__(self, model: EmbeddingCall, embedding_factory: EmbeddingFactory):
        self.model = model
        self.embedding_factory = embedding_factory

    def create(self, embedding: EmbeddingDomain) -> EmbeddingDomain:
        embedding_instance = self.model.objects.create(
            embedding=embedding.embedding,
            model=embedding.model,
            total_tokens=embedding.total_tokens,
            prompt_used_tokens=embedding.prompt_used_tokens,
        )
        return self.embedding_factory.build_from_model(embedding_instance)
