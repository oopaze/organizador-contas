import json
import logging
import time
import traceback

from openai import OpenAI
from openai.types.chat import ChatCompletion

from modules.ai.domains.ai_request import AIRequestDomain
from modules.ai.factories.ai_request import AIRequestFactory

logger = logging.getLogger(__name__)


def mask_api_key(api_key: str) -> str:
    """Mask API key for logging, showing only first 8 and last 4 chars."""
    if not api_key or len(api_key) < 16:
        return "***"
    return f"{api_key[:8]}...{api_key[-4:]}"


class LLMGateway:
    _client: OpenAI = None

    def __init__(self, api_key: str, base_url: str, ai_request_factory: AIRequestFactory):
        self.api_key = api_key
        self.base_url = base_url
        self.ai_request_factory = ai_request_factory
        logger.info("LLMGateway initialized - base_url: %s, api_key: %s",
                    base_url, mask_api_key(api_key))

    def get_client(self) -> OpenAI:
        if self._client is None:
            logger.debug("LLMGateway.get_client - Creating new OpenAI client for %s", self.base_url)
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client

    @property
    def client(self) -> OpenAI:
        return self.get_client()

    def ask(self, ai_request: AIRequestDomain) -> ChatCompletion:
        logger.info("LLMGateway.ask - Starting request to %s", self.base_url)
        logger.info("LLMGateway.ask - Model: %s, User: %s", ai_request.model, ai_request.user_id)
        logger.debug("LLMGateway.ask - Temperature: %s, Tools: %s",
                     ai_request.temperature if ai_request.temperature_enabled else None,
                     bool(ai_request.tool_configs))

        start_time = time.time()
        try:
            # Build request params, only include response_format if it's not the default
            request_params = {
                "model": ai_request.model,
                "messages": ai_request.prompt,
                "temperature": ai_request.temperature if ai_request.temperature_enabled else None,
                "tools": ai_request.tool_configs,
                "tool_choice": ai_request.tool_choice,
                "user": str(ai_request.user_id),
            }

            # Only add response_format for providers that support it (not Google)
            # Google's OpenAI compatibility layer doesn't support response_format properly
            if ai_request.response_format and ai_request.response_format != "text":
                # Check if it's already a dict or needs to be converted
                if isinstance(ai_request.response_format, str):
                    request_params["response_format"] = {"type": ai_request.response_format}
                else:
                    request_params["response_format"] = ai_request.response_format

            logger.debug("LLMGateway.ask - Request params: %s",
                         {k: v for k, v in request_params.items() if k != "messages"})

            completion = self.client.chat.completions.create(**request_params)

            elapsed = time.time() - start_time
            logger.info("LLMGateway.ask - SUCCESS in %.2fs - finish_reason: %s",
                        elapsed, completion.choices[0].finish_reason)

            if completion.choices[0].finish_reason == "tool_calls":
                logger.info("LLMGateway.ask - Processing tool call")
                assistant_prompt = completion.choices[0].message.model_dump(exclude_none=True)
                tool_call = completion.choices[0].message.tool_calls[0]
                logger.info("LLMGateway.ask - Tool: %s", tool_call.function.name)

                tool = ai_request.get_tool_by_name(tool_call.function.name)
                function_args = json.loads(tool_call.function.arguments)
                ai_request.add_tool_output(tool_call, assistant_prompt, tool.execute(**function_args))
                tool_ai_request = self.ai_request_factory.build_for_tool_request(ai_request.prompt, ai_request)
                return self.ask(tool_ai_request)

            return completion

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error("LLMGateway.ask - ERROR after %.2fs - base_url: %s, model: %s",
                         elapsed, self.base_url, ai_request.model)
            logger.error("LLMGateway.ask - Error type: %s, Message: %s", type(e).__name__, str(e))
            logger.error("LLMGateway.ask - Traceback:\n%s", traceback.format_exc())
            raise
