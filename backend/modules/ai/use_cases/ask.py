import logging

from modules.ai.domains.ai_request import AIRequestDomain
from modules.ai.domains.ai_response import AIResponseDomain
from modules.ai.factories.ai_request import AIRequestFactory
from modules.ai.factories.ai_response import AIResponseFactory
from modules.ai.services.llm import LLMService
from modules.ai.repositories.ai_call import AICallRepository
from modules.ai.types import LlmModels
from modules.ai.exceptions import LLMGatewayException

logger = logging.getLogger(__name__)


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
        user_id: int,
        model: str = LlmModels.GOOGLE_GEMINI_2_5_FLASH_LITE.name,
        tools: list = [],
        chat_session_key: str = None,
        temperature: float = 0.1,
        tool_choice: str = None,
        history: str = "",
        response_format: str = None,
    ) -> AIResponseDomain:
        logger.info(f"[AskUseCase] Starting execute with model: {model}, user_id: {user_id}")
        logger.info(f"[AskUseCase] Prompt length: {len(prompt)} parts, response_format: {response_format}")

        ai_request = self.ai_request_factory.build(
            prompt=prompt,
            model=model,
            tools=tools,
            chat_session_key=chat_session_key,
            temperature=temperature,
            user_id=user_id,
            tool_choice=tool_choice,
            history=history,
            response_format=response_format,
        )
        logger.info(f"[AskUseCase] AI request built, calling LLM...")
        response = self.ask_ai(ai_request)
        logger.info(f"[AskUseCase] LLM response received, saving to repository...")
        ai_response = self.ai_call_repository.create(response, user_id)
        logger.info(f"[AskUseCase] Response saved with id: {ai_response.id}")
        return ai_response.id

    def ask_ai(self, ai_request: AIRequestDomain) -> AIResponseDomain:
        try:
            logger.info(f"[AskUseCase.ask_ai] Calling LLM service...")
            llm_response = self.llm_service.ask(ai_request)
            logger.info(f"[AskUseCase.ask_ai] LLM service returned successfully")
            return self.ai_response_factory.build_from_llm_response(llm_response, ai_request)
        except LLMGatewayException as e:
            logger.error(f"[AskUseCase.ask_ai] LLMGatewayException: {e}")
            import traceback
            logger.error(f"[AskUseCase.ask_ai] Traceback: {traceback.format_exc()}")
            return self.ai_request_factory.build_empty_response(ai_request)
