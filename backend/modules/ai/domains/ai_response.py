from google.genai.types import GenerateContentResponse


class AIResponseDomain:
    def __init__(
        self, 
        total_tokens: int = None,
        input_used_tokens: int = None,
        output_used_tokens: int = None,
        prompt: list[str] = None,
        response: dict = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        google_response: GenerateContentResponse = None,
    ):
        self.total_tokens = total_tokens
        self.input_used_tokens = input_used_tokens
        self.output_used_tokens = output_used_tokens
        self.prompt = prompt
        self.response = response
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.google_response = google_response
