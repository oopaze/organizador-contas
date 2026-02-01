from typing import TYPE_CHECKING

from modules.ai.chat.domains import MessageDomain, AICallDomain
from modules.ai.chat.models import Message

if TYPE_CHECKING:
    from modules.ai.chat.factories import AICallFactory


class MessageFactory:
    def __init__(self, ai_call_factory: "AICallFactory"):
        self.ai_call_factory = ai_call_factory

    def build_from_model(self, model: Message) -> MessageDomain:
        return MessageDomain(
            role=model.role,
            content=model.content,
            ai_call=self.ai_call_factory.build_from_model(model.ai_call) if model.ai_call else None,
            conversation_id=model.conversation_id,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            embedding_id=model.embedding_id,
            user_message=self.build_from_model(model.user_message) if model.user_message else None,
            is_error=model.is_error,
        )
    
    def build(self, content: str, conversation_id: int, role: str = Message.Role.HUMAN) -> MessageDomain:
        return MessageDomain(
            role=role,
            content=content,
            conversation_id=conversation_id,
        )
    
    def build_ai_message(self, ai_call: AICallDomain, conversation_id: int, user_message: MessageDomain) -> MessageDomain:
        return MessageDomain(
            role=Message.Role.ASSISTANT,
            content=ai_call.response,
            conversation_id=conversation_id,
            ai_call=ai_call,
            user_message=user_message,
            is_error=ai_call.is_error,
        )
