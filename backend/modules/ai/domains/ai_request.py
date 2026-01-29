from google.genai.types import ToolListUnion


class AIRequestDomain:
    def __init__(
        self,
        prompt: list[str] = None,
        model: str = None,
        attachments: list[str] = None,
        tools: list[ToolListUnion] = None,
        history: list[dict] = None,
    ):
        self.prompt = prompt
        self.model = model
        self.attachments = attachments
        self.tools = tools
        self.history = history

    def set_attachments(self, attachments: list[str]):
        self.attachments = attachments

    def set_tools(self, tools: list[ToolListUnion]):
        self.tools = tools
