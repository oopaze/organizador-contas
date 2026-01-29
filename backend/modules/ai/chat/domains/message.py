from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.ai.chat.domains.ai_call import AICallDomain


class MessageDomain:
    MIN_CONTENT_LENGTH_FOR_EMBEDDING = 20

    def __init__(
        self,
        role: str,
        content: str,
        conversation_id: int = None,
        ai_call: "AICallDomain" = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        embedding_id: int = None,
    ):
        self.role = role
        self.content = content
        self.conversation_id = conversation_id
        self.ai_call = ai_call
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.embedding_id = embedding_id

    def update_ai_call(self, ai_call: "AICallDomain"):
        self.ai_call = ai_call

    def update_embedding_id(self, embedding_id: int):
        self.embedding_id = embedding_id

    def should_create_embedding(self) -> bool:
        content_not_none = self.content is not None
        content_match_min_length = len(self.content) > self.MIN_CONTENT_LENGTH_FOR_EMBEDDING
        return content_not_none and content_match_min_length
