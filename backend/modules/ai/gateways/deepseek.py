from openai import OpenAI
from openai.types.chat import ChatCompletion

from modules.ai.domains.ai_request import AIRequestDomain


class DeepSeekModels:
    # Chat / uso geral
    DEEPSEEK_CHAT = "deepseek-chat"
    DEEPSEEK_V3 = "deepseek-v3"
    DEEPSEEK_V3_1 = "deepseek-v3.1"
    DEEPSEEK_V3_2 = "deepseek-v3.2"

    # Raciocínio avançado
    DEEPSEEK_REASONER = "deepseek-reasoner"
    DEEPSEEK_R1 = "deepseek-r1"
    DEEPSEEK_R1_0528 = "deepseek-r1-0528"

    # Código
    DEEPSEEK_CODER_V1 = "deepseek-coder-v1"
    DEEPSEEK_CODER_V2 = "deepseek-coder-v2"

    # Matemática / provas formais
    DEEPSEEK_MATH = "deepseek-math"
    DEEPSEEK_MATH_V2 = "deepseek-math-v2"
    DEEPSEEK_PROVER_V2 = "deepseek-prover-v2"


class DeepSeekLLMGateway:
    _client: OpenAI = None

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

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

    def _build_messages(self, ai_request: AIRequestDomain) -> list[dict]:
        messages = []

        if ai_request.history:
            for msg in ai_request.history:
                if hasattr(msg, "role") and hasattr(msg, "parts"):
                    role = msg.role if msg.role != "model" else "assistant"
                    content = msg.parts[0].text if msg.parts else ""
                    messages.append({"role": role, "content": content})
                elif isinstance(msg, dict):
                    role = msg.get("role", "user")
                    role = role if role != "model" else "assistant"
                    messages.append({"role": role, "content": msg.get("content", "")})

        prompt_content = (
            ai_request.prompt
            if isinstance(ai_request.prompt, str)
            else "\n".join(ai_request.prompt)
        )
        messages.append({"role": "user", "content": prompt_content})

        return messages

    def _convert_tools(self, tools: list) -> list[dict] | None:
        """Convert Google-style tools (callables) to OpenAI function format."""
        if not tools:
            return None

        openai_tools = []
        for tool in tools:
            if callable(tool):
                func_name = tool.__name__
                func_doc = tool.__doc__ or ""
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": func_name,
                        "description": func_doc,
                        "parameters": {"type": "object", "properties": {}},
                    },
                })
            elif isinstance(tool, dict):
                openai_tools.append(tool)

        return openai_tools if openai_tools else None

    def ask(self, ai_request: AIRequestDomain) -> ChatCompletion:
        messages = self._build_messages(ai_request)
        tools = self._convert_tools(ai_request.tools)

        kwargs = {
            "model": ai_request.model,
            "messages": messages,
            "temperature": 0.1,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        else:
            kwargs["response_format"] = {"type": "json_object"}

        return self.client.chat.completions.create(**kwargs)
