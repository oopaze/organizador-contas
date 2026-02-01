import logging

from openai.types.chat import ChatCompletion

from modules.ai.domains import AIRequestDomain
from modules.ai.types import LlmModels, LlmProviders
from modules.ai.gateways import LLMGateway
from modules.ai.exceptions import LLMGatewayException

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, deepseek_llm_gateway: LLMGateway, google_llm_gateway: LLMGateway, openai_llm_gateway: LLMGateway):
        self._gateways = {
            LlmProviders.DEEPSEEK.name: deepseek_llm_gateway,
            LlmProviders.GOOGLE.name: google_llm_gateway,
            LlmProviders.OPENAI.name: openai_llm_gateway,
        }

    def ask(self, ai_request: AIRequestDomain) -> ChatCompletion:
        try:
            model_info = LlmModels.get_model(ai_request.model)
            provider = model_info.provider
            logger.info(f"[LLMService] Requesting model: {ai_request.model}, provider: {provider}")

            gateway = self._gateways[provider]
            logger.info(f"[LLMService] Calling gateway.ask()...")
            result = gateway.ask(ai_request)
            logger.info(f"[LLMService] Gateway returned successfully")
            return result
        except Exception as e:
            logger.error(f"[LLMService] Error calling LLM: {type(e).__name__}: {e}")
            raise LLMGatewayException(f"LLM Gateway could not process the request: {e}")
