from typing import TYPE_CHECKING

from modules.ai.chat.domains import MessageDomain
from modules.ai.chat.models import Message

if TYPE_CHECKING:
    from modules.ai.chat.serializers import AICallSerializer


MESSAGE_AS_HISTORY = """
Message from {role}: {content}
"""


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
    
    def serialize_for_history(self, message: "MessageDomain") -> str:
        return MESSAGE_AS_HISTORY.format(role=message.role, content=message.content)
    
    def serialize_many_for_history(self, messages: list["MessageDomain"]) -> list[str]:
        return "".join([self.serialize_for_history(message) for message in messages])
