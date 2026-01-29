from google import genai
from google.genai import types
from google.genai.types import GenerateContentResponse

from modules.ai.domains.ai_request import AIRequestDomain


class GoogleModels:
    GEMINI_3_PRO_PREVIEW = "gemini-3-pro-preview"
    GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"
    GEMINI_3_PRO_IMAGE_PREVIEW = "gemini-3-pro-image-preview"

    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_FLASH_LITE = "gemini-2.5-flash-lite"


class GoogleLLMGateway:
    _client = None

    def __init__(self, api_key):
        self.api_key = api_key

    def get_config(self):
        return types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
            candidate_count=1,
        )

    def get_client(self):
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def ask(
        self, ai_request: AIRequestDomain,
    ) -> GenerateContentResponse:
        client = self.get_client()
        response = client.models.generate_content(
            contents=ai_request.prompt, model=ai_request.model, config=self.get_config()
        )
        return response

    def ask_with_attachment(
        self, ai_request: AIRequestDomain,
    ) -> GenerateContentResponse:
        client = self.get_client()
        attachments = [client.files.upload(file=file_url) for file_url in ai_request.attachments]
        return self.ask([*attachments, *ai_request.prompt], ai_request.model)
