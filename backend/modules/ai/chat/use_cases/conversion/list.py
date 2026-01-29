from modules.ai.chat.repositories import ConversationRepository
from modules.ai.chat.serializers import ConversationSerializer


class ListConversationsUseCase:
    def __init__(self, conversation_repository: ConversationRepository, conversation_serializer: ConversationSerializer):
        self.conversation_repository = conversation_repository
        self.conversation_serializer = conversation_serializer

    def execute(self, user_id: int) -> list[dict]:
        conversations = self.conversation_repository.get_all_by_user_id(user_id)
        return [self.conversation_serializer.serialize(conversation) for conversation in conversations]
