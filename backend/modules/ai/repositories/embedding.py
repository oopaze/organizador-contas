from modules.ai.domains.embedding import EmbeddingDomain
from modules.ai.factories.embedding import EmbeddingFactory
from modules.ai.models import EmbeddingCall
from modules.ai.chat.models import Message


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
    
    def get_all_by_user_id(self, user_id: int, due_date_start: str = None, due_date_end: str = None):
        messages_from_user = Message.objects.filter(conversation__user_id=user_id, embedding__isnull=False).values_list("embedding_id", flat=True)
        embedding_instances = self.model.objects.filter(id__in=messages_from_user)

        if due_date_start and due_date_end:
            embedding_instances = embedding_instances.filter(created_at__gte=due_date_start, created_at__lte=due_date_end)

        return [self.embedding_factory.build_from_model(embedding) for embedding in embedding_instances]
