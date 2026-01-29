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
        )

    def build(self, title: str) -> ConversationDomain:
        return ConversationDomain(title=title)
    
    def build_from_ai_call(self, ai_call: AICallDomain) -> ConversationDomain:
        title = ai_call.response.get("title", "Sem título")
        return ConversationDomain(title=title, ai_call=ai_call)
