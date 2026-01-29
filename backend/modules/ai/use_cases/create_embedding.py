from modules.ai.gateways.openai_embedding import OpenAIEmbeddingGateway, EmbeddingModels
from modules.ai.repositories.embedding import EmbeddingRepository
from modules.ai.factories.embedding import EmbeddingFactory
from modules.ai.domains.embedding import EmbeddingDomain


class CreateEmbeddingUseCase:
    def __init__(
        self,
        openai_embedding_gateway: OpenAIEmbeddingGateway,
        embedding_repository: EmbeddingRepository,
        embedding_factory: EmbeddingFactory,
    ):
        self.openai_embedding_gateway = openai_embedding_gateway
        self.embedding_repository = embedding_repository
        self.embedding_factory = embedding_factory

    def execute(self, text: str, model: str = EmbeddingModels.TEXT_EMBEDDING_3_SMALL) -> EmbeddingDomain:
        embedding_model_response = self.openai_embedding_gateway.generate_embedding(text, model)
        embedding = self.embedding_repository.create(
            self.embedding_factory.build_from_embedding_model_response(embedding_model_response, model)
        )
        return embedding.id
