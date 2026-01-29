class EmbeddingCallDomain:
    def __init__(
        self,
        embedding: list[float] = None,
        model: str = None,
        total_tokens: int = None,
        prompt_used_tokens: int = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
    ):
        self.embedding = embedding
        self.model = model
        self.total_tokens = total_tokens
        self.prompt_used_tokens = prompt_used_tokens
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
