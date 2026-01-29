from modules.ai.domains.ai_request import AIRequestDomain


class AIRequestFactory:
    def build(self, prompt: list[str], model: str, attachments: list[str] = None) -> AIRequestDomain:
        return AIRequestDomain(prompt=prompt, model=model, attachments=attachments)
