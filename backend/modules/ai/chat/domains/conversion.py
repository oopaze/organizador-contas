from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.ai.chat.domains.message import MessageDomain
    from modules.ai.chat.domains.ai_call import AICallDomain


class ConversationDomain:
    SESSION_PREFIX = "conversation_"

    def __init__(
        self,
        title: str = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        messages: list["MessageDomain"] = [],
        ai_call: "AICallDomain" = None,
        user_id: int = None,
    ):
        self.title = title
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.messages = messages
        self.ai_call = ai_call
        self.user_id = user_id
        self.chat_session_key = self.SESSION_PREFIX + str(self.id)

    def update_ai_call(self, ai_call: "AICallDomain"):
        self.ai_call = ai_call
        self.title = ai_call.response or f"Conversa #{self.id}"
