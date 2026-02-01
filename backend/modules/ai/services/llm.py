from openai.types.chat import ChatCompletion

from modules.ai.domains import AIRequestDomain
from modules.ai.types import LlmModels, LlmProviders
from modules.ai.gateways import LLMGateway
from modules.ai.exceptions import LLMGatewayException


class LLMService:
    def __init__(self, deepseek_llm_gateway: LLMGateway, google_llm_gateway: LLMGateway, openai_llm_gateway: LLMGateway):
        self._gateways = {
            LlmProviders.DEEPSEEK.name: deepseek_llm_gateway,
            LlmProviders.GOOGLE.name: google_llm_gateway,
            LlmProviders.OPENAI.name: openai_llm_gateway,
        }

    def ask(self, ai_request: AIRequestDomain) -> ChatCompletion:
        try:
            gateway = self._gateways[LlmModels.get_model(ai_request.model).provider]
            return gateway.ask(ai_request)
        except Exception as e:
            print("LLMService.ask.error", e)
            raise LLMGatewayException("LLM Gateway could not process the request.")
