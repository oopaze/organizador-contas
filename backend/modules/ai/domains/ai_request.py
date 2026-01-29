class AIRequestDomain:
    def __init__(
        self,
        prompt: list[str] = None,
        model: str = None,
        attachments: list[str] = None,
    ):
        self.prompt = prompt
        self.model = model
        self.attachments = attachments
