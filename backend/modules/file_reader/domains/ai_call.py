class AICallDomain:
    def __init__(
        self,
        prompt: list[str] = None,
        response: dict = None,
        total_tokens: int = None,
        input_used_tokens: int = None,
        output_used_tokens: int = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        model: str = None,
    ):
        self.prompt = prompt
        self.response = response
        self.total_tokens = total_tokens
        self.input_used_tokens = input_used_tokens
        self.output_used_tokens = output_used_tokens
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.model = model
