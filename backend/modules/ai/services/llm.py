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
        try:
            gateway = self._gateways[provider]
            logger.debug("LLMService.ask - Using gateway for provider: %s", provider)

            return gateway.ask(ai_request)
        except Exception as e:
            logger.error("LLMService.ask - ERROR - Model: %s, Provider: %s, Error: %s",
                         ai_request.model, provider, str(e))
            logger.error("LLMService.ask - Traceback:\n%s", traceback.format_exc())
            raise LLMGatewayException("LLM Gateway could not process the request.")
