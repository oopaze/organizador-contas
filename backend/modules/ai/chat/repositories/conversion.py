from modules.ai.chat.domains import ConversationDomain
from modules.ai.chat.factories import ConversationFactory
from modules.ai.chat.models import Conversation


class ConversationRepository:
    def __init__(self, model: Conversation, conversation_factory: ConversationFactory):
        self.model = model
        self.conversation_factory = conversation_factory

    def create(self, conversation: ConversationDomain, user_id: int) -> ConversationDomain:
        conversation_instance = self.model.objects.create(title=conversation.title, ai_call_id=conversation.ai_call.id, user_id=user_id)
        return self.conversation_factory.build_from_model(conversation_instance)
    
    def get(self, conversation_id: int, user_id: int) -> ConversationDomain:
        conversation_instance = self.model.objects.get(id=conversation_id, user_id=user_id)
        return self.conversation_factory.build_from_model(conversation_instance)
    
    def get_all_by_user_id(self, user_id: int) -> list[ConversationDomain]:
        conversation_instances = self.model.objects.filter(user_id=user_id)
        return [self.conversation_factory.build_from_model(conversation) for conversation in conversation_instances]
