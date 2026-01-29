from google import genai
from google.genai import types
from google.genai.types import GenerateContentResponse, ToolListUnion

from modules.ai.domains.ai_request import AIRequestDomain


class GoogleModels:
    GEMINI_3_PRO_PREVIEW = "gemini-3-pro-preview"
    GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"
    GEMINI_3_PRO_IMAGE_PREVIEW = "gemini-3-pro-image-preview"

    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_FLASH_LITE = "gemini-2.5-flash-lite"


class GoogleLLMGateway:
    _client: genai.Client = None

    def __init__(self, api_key):
        self.api_key = api_key

    def get_config(self, tools: list[ToolListUnion] = []):
        return types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
            candidate_count=1,
            tools=tools,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False,
                ignore_call_history=True,
            ),
        )

    def get_client(self):
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client
    
    @property
    def client(self):
        return self.get_client()

    def ask(self, ai_request: AIRequestDomain) -> GenerateContentResponse:
        chat_session = self.client.chats.create(
            model=ai_request.model, 
            config=self.get_config(tools=ai_request.tools),
            history=ai_request.history,
        )
        return chat_session.send_message(ai_request.prompt)

    def ask_with_attachment(self, ai_request: AIRequestDomain) -> GenerateContentResponse:
        attachments = [self.client.files.upload(file=file_url) for file_url in ai_request.attachments]
        ai_request.set_attachments(attachments)
        return self.ask(ai_request)
