from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.ai.chat.domains.message import MessageDomain
    from modules.ai.chat.domains.ai_call import AICallDomain


class ConversationDomain:
    def __init__(
        self,
        title: str = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        messages: list["MessageDomain"] = [],
        ai_call: "AICallDomain" = None,
    ):
        self.title = title
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.messages = messages
        self.ai_call = ai_call
