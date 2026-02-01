from modules.ai.chat.domains import ConversationDomain, AICallDomain
from modules.ai.chat.models import Conversation


class ConversationFactory:
    def build_from_model(self, model: Conversation) -> ConversationDomain:
        return ConversationDomain(
            title=model.title,
            ai_call=model.ai_call,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            user_id=model.user_id,
        )

    def build(self, title: str = None, user_id: int = None) -> ConversationDomain:
        return ConversationDomain(title=title, user_id=user_id)
    
    def build_from_ai_call(self, ai_call: AICallDomain) -> ConversationDomain:
        title = ai_call.response or "Sem título"
        return ConversationDomain(title=title, ai_call=ai_call)
