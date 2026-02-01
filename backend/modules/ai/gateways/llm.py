import json

from openai import OpenAI
from openai.types.chat import ChatCompletion

from modules.ai.domains.ai_request import AIRequestDomain
from modules.ai.factories.ai_request import AIRequestFactory


class LLMGateway:
    _client: OpenAI = None

    def __init__(self, api_key: str, base_url: str, ai_request_factory: AIRequestFactory):
        self.api_key = api_key
        self.base_url = base_url
        self.ai_request_factory = ai_request_factory

    def get_client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client

    @property
    def client(self) -> OpenAI:
        return self.get_client()

    def ask(self, ai_request: AIRequestDomain) -> ChatCompletion:
        completion = self.client.chat.completions.create(
            model=ai_request.model,
            messages=ai_request.prompt,
            temperature=ai_request.temperature if ai_request.temperature_enabled else None,
            tools=ai_request.tool_configs,
            tool_choice=ai_request.tool_choice,
            user=str(ai_request.user_id),
            response_format={"type": ai_request.response_format},
        )

        if completion.choices[0].finish_reason == "tool_calls":
            assistant_prompt = completion.choices[0].message.model_dump(exclude_none=True)
            tool_call = completion.choices[0].message.tool_calls[0]
            tool = ai_request.get_tool_by_name(tool_call.function.name)
            function_args = json.loads(tool_call.function.arguments)
            ai_request.add_tool_output(tool_call, assistant_prompt, tool.execute(**function_args))
            tool_ai_request = self.ai_request_factory.build_for_tool_request(ai_request.prompt, ai_request)
            return self.ask(tool_ai_request)
        return completion
