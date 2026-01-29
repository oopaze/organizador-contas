from modules.ai.domains.ai_request import AIRequestDomain
from modules.ai.domains.ai_response import AIResponseDomain
from modules.ai.factories.ai_request import AIRequestFactory
from modules.ai.factories.ai_response import AIResponseFactory
from modules.ai.gateways.gemini import GoogleLLMGateway
from modules.ai.repositories.ai_call import AICallRepository


class AskUseCase:
    def __init__(
        self,
        ai_request_factory: AIRequestFactory,
        ai_response_factory: AIResponseFactory,
        google_llm_gateway: GoogleLLMGateway,
        ai_call_repository: AICallRepository,
    ):
        self.ai_request_factory = ai_request_factory
        self.ai_response_factory = ai_response_factory
        self.google_llm_gateway = google_llm_gateway
        self.ai_call_repository = ai_call_repository

    def execute(
        self,
        prompt: list[str],
        model: str,
        attachments: list[str] = None,
    ) -> AIResponseDomain:
        ai_request = self.ai_request_factory.build(prompt, model, attachments)
        response = self.ask_ai(ai_request)
        ai_response = self.ai_call_repository.create(response)
        return ai_response.id
    
    def ask_ai(self, ai_request: AIRequestDomain) -> AIResponseDomain:
        ask_fn = (
            self.google_llm_gateway.ask_with_attachment
            if ai_request.attachments
            else self.google_llm_gateway.ask
        )

        return self.ai_response_factory.build_from_llm_response(
            ask_fn(ai_request),
            ai_request.prompt,
        )
