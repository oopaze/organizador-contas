from pgvector.django import CosineDistance

from modules.ai.chat.domains import MessageDomain
from modules.ai.chat.factories import MessageFactory
from modules.ai.chat.models import Message


class MessageRepository:
    HISTORY_THRESHOLD = 0.3

    def __init__(self, model: Message, message_factory: MessageFactory):
        self.model = model
        self.message_factory = message_factory

    def create(self, message: MessageDomain) -> MessageDomain:
        message_instance = self.model.objects.create(
            role=message.role,
            content=message.content,
            conversation_id=message.conversation_id,
            ai_call_id=message.ai_call.id,
            embedding_id=message.embedding_id,
        )
        return self.message_factory.build_from_model(message_instance)
    
    def update(self, message: MessageDomain) -> MessageDomain:
        message_instance = self.model.objects.get(id=message.id)
        message_instance.embedding_id = message.embedding_id
        message_instance.save()
        return self.message_factory.build_from_model(message_instance)

    def get_all_by_conversation_id(self, conversation_id: int, user_id: int) -> list[MessageDomain]:
        message_instances = self.model.objects.filter(conversation_id=conversation_id, conversation__user_id=user_id)
        return [self.message_factory.build_from_model(message) for message in message_instances]
    
    def get_contextualized_messages_from_conversation(
        self, 
        embedding: list[float], 
        conversation_id: int, 
        limit: int = 20,
    ) -> list[MessageDomain]:
        message_instances = self.model.objects.filter(
            conversation_id=conversation_id, 
            embedding__isnull=False,
        ).alias(
            distance=CosineDistance("embedding__embedding", embedding)
        ).filter(
            distance__lt=self.HISTORY_THRESHOLD
        ).order_by("distance")[:limit]
        return [self.message_factory.build_from_model(message) for message in message_instances]
