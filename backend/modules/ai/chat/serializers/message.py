from typing import TYPE_CHECKING

from modules.ai.chat.domains import MessageDomain

if TYPE_CHECKING:
    from modules.ai.chat.serializers import AICallSerializer


class MessageSerializer:
    def __init__(self, ai_call_serializer: "AICallSerializer"):
        self.ai_call_serializer = ai_call_serializer

    def serialize(self, message: "MessageDomain") -> dict:
        ai_call = self.ai_call_serializer.serialize_without_prompt_and_response(message.ai_call) if message.ai_call else None
        return {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "ai_call": ai_call,
            "created_at": message.created_at,
            "updated_at": message.updated_at,
        }
    
    def serialize_only_content_and_role(self, message: "MessageDomain") -> dict:
        return {
            "role": message.role,
            "content": message.content,
        }
