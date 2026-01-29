from openai import OpenAI
from openai.types import CreateEmbeddingResponse


class EmbeddingModels:
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"


class OpenAIEmbeddingGateway:
    _client: OpenAI = None

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_client(self):
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key)
        return self._client
    
    @property
    def client(self):
        return self.get_client()

    def generate_embedding(self, text: str, model: str = EmbeddingModels.TEXT_EMBEDDING_3_SMALL) -> CreateEmbeddingResponse:
        return self.client.embeddings.create(input=text, model=model)
