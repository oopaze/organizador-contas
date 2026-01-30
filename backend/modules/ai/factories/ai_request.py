from google.genai import types

from modules.ai.domains.ai_request import AIRequestDomain


class AIRequestFactory:
    def build(
        self, 
        prompt: list[str], 
        model: str, 
        attachments: list[str] = None, 
        history: list[dict] = [], 
        tools: list = []
    ) -> AIRequestDomain:
        return AIRequestDomain(
            prompt=prompt, 
            model=model, 
            attachments=attachments, 
            tools=tools,
            history=[
                types.Content(
                    role=message["role"],
                    parts=[types.Part.from_text(text=message["content"])]
                )
                for message in history
            ]
        )
