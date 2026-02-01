from modules.ai.domains.ai_request import AIRequestDomain
from modules.ai.domains.ai_response import AIResponseDomain
from modules.ai.factories.ai_request import AIRequestFactory
from modules.ai.factories.ai_response import AIResponseFactory
from modules.ai.services.llm import LLMService
from modules.ai.repositories.ai_call import AICallRepository
from modules.ai.types import LlmModels
from modules.ai.exceptions import LLMGatewayException


class AskUseCase:
    def __init__(
        self,
        ai_request_factory: AIRequestFactory,
        ai_response_factory: AIResponseFactory,
        ai_call_repository: AICallRepository,
        llm_service: LLMService,
    ):
        self.ai_request_factory = ai_request_factory
        self.ai_response_factory = ai_response_factory
        self.ai_call_repository = ai_call_repository
        self.llm_service = llm_service

    def execute(
        self,
        prompt: list[str],
        model: str = LlmModels.GOOGLE_GEMINI_2_5_FLASH_LITE.name,
        tools: list = [],
        chat_session_key: str = None,
        user_id: int = None,
        temperature: float = 0.1,
        tool_choice: str = "auto",
        history: str = "",
    ) -> AIResponseDomain:
        ai_request = self.ai_request_factory.build(
            prompt=prompt,
            model=model,
            tools=tools,
            chat_session_key=chat_session_key,
            user_id=user_id,
            temperature=temperature,
            tool_choice=tool_choice,
            history=history,
        )
        response = self.ask_ai(ai_request)
        ai_response = self.ai_call_repository.create(response)
        return ai_response.id
    
    def ask_ai(self, ai_request: AIRequestDomain) -> AIResponseDomain:
        try:
            return self.ai_response_factory.build_from_llm_response(
                self.llm_service.ask(ai_request),
                ai_request,
            )
        except LLMGatewayException as e:
            return self.ai_request_factory.build_empty_response(ai_request)
