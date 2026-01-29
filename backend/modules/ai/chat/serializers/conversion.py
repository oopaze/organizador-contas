from modules.ai.chat.domains import ConversationDomain
from modules.ai.chat.serializers import MessageSerializer


class ConversationSerializer:
    def __init__(self, message_serializer: "MessageSerializer"):
        self.message_serializer = message_serializer

    def serialize(self, conversation: "ConversationDomain") -> dict:
        return {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "messages": [self.message_serializer.serialize(message) for message in conversation.messages],
        }
