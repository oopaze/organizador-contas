from modules.ai.chat.repositories import MessageRepository
from modules.ai.chat.serializers import MessageSerializer


class ListMessagesUseCase:
    def __init__(self, message_repository: MessageRepository, message_serializer: MessageSerializer):
        self.message_repository = message_repository
        self.message_serializer = message_serializer

    def execute(self, conversation_id: int, user_id: int) -> list[dict]:
        messages = self.message_repository.get_all_by_conversation_id(conversation_id, user_id)
        return [self.message_serializer.serialize(message) for message in messages]
