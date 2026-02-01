import logging
import time
import traceback

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
        logger.info("LLMService initialized with gateways: %s", list(self._gateways.keys()))

    def ask(self, ai_request: AIRequestDomain) -> ChatCompletion:
        model_info = LlmModels.get_model(ai_request.model)
        provider = model_info.provider

        logger.info("LLMService.ask - Model: %s, Provider: %s, User: %s",
                    ai_request.model, provider, ai_request.user_id)

        start_time = time.time()
        try:
            gateway = self._gateways[provider]
            logger.debug("LLMService.ask - Using gateway for provider: %s", provider)

            result = gateway.ask(ai_request)

            elapsed = time.time() - start_time
            logger.info("LLMService.ask - SUCCESS in %.2fs - Model: %s, Provider: %s",
                        elapsed, ai_request.model, provider)
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error("LLMService.ask - ERROR after %.2fs - Model: %s, Provider: %s, Error: %s",
                         elapsed, ai_request.model, provider, str(e))
            logger.error("LLMService.ask - Traceback:\n%s", traceback.format_exc())
            raise LLMGatewayException("LLM Gateway could not process the request.")
