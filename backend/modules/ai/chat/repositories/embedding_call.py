from modules.ai.chat.domains import EmbeddingCallDomain
from modules.ai.chat.factories import EmbeddingCallFactory
from modules.ai.models import EmbeddingCall


class EmbeddingCallRepository:
    def __init__(self, model: EmbeddingCall, embedding_call_factory: EmbeddingCallFactory):
        self.model = model
        self.embedding_call_factory = embedding_call_factory

    def get(self, embedding_call_id: str) -> EmbeddingCallDomain:
        embedding_call_instance = self.model.objects.get(id=embedding_call_id)
        return self.embedding_call_factory.build_from_model(embedding_call_instance)
