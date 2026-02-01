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
            user_message_id=message.user_message.id if message.user_message else None,
            is_error=message.is_error,
        )
        return self.message_factory.build_from_model(message_instance)
    
    def update(self, message: MessageDomain) -> MessageDomain:
        message_instance = self.model.objects.get(id=message.id)
        message_instance.embedding_id = message.embedding_id
        message_instance.save()
        return self.message_factory.build_from_model(message_instance)

    def get_all_by_conversation_id(self, conversation_id: int, user_id: int) -> list[MessageDomain]:
        message_instances = self.model.objects.filter(conversation_id=conversation_id, conversation__user_id=user_id, is_error=False)
        return [self.message_factory.build_from_model(message) for message in message_instances]
    
    def get_history_from_conversation(
        self, 
        conversation_id: int, 
        limit: int = 20,
    ) -> list[MessageDomain]:
        message_instances = self.model.objects.filter(conversation_id=conversation_id, is_error=False).order_by("-created_at")[:limit]
        return [self.message_factory.build_from_model(message) for message in message_instances]
    
    def get_contextualized_messages_from_conversation(
        self, 
        embedding: list[float], 
        conversation_id: int, 
        limit: int = 20,
    ) -> list[MessageDomain]:
        minimum_history_messages = self.model.objects.filter(conversation_id=conversation_id, is_error=False).order_by("-created_at")[:10]
        minimum_history_messages_id = [message.id for message in minimum_history_messages]

        message_instances = (
            self.model.objects
            .exclude(id__in=minimum_history_messages_id)
            .filter(
                conversation_id=conversation_id, 
                embedding__isnull=False,
                is_error=False,
            ).alias(
                distance=CosineDistance("embedding__embedding", embedding)
            ).filter(
                distance__lt=self.HISTORY_THRESHOLD
            ).order_by("distance")[:limit - 10]
        )

        context_message = [self.message_factory.build_from_model(message) for message in message_instances]
        context_message.extend([self.message_factory.build_from_model(message) for message in minimum_history_messages])
        return context_message 
