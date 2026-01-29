from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.ai.chat.domains.ai_call import AICallDomain


class MessageDomain:
    def __init__(
        self,
        role: str,
        content: str,
        conversation_id: int = None,
        ai_call: "AICallDomain" = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
    ):
        self.role = role
        self.content = content
        self.conversation_id = conversation_id
        self.ai_call = ai_call
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at

    def update_ai_call(self, ai_call: "AICallDomain"):
        self.ai_call = ai_call
