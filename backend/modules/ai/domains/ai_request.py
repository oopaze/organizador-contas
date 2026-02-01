from modules.transactions.use_cases.get_tools_for_ai import ToolInterface
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCallUnion
from modules.ai.types import LlmModels
from modules.ai.prompts import HISTORY

class AIRequestTypes:
    COMPLETION = "completion"
    TOOL_CALL = "tool_call"


class AIRequestDomain:
    tools: list[ToolInterface] = None
    tool_configs: list[dict] = None

    def __init__(
        self,
        prompt: list[dict] = None,
        model: str = None,
        attachments: list[str] = None,
        tools: list[ToolInterface] = None,
        chat_session_key = None,
        user_id: int = None,
        temperature: float = 0.1,
        tool_choice: str = None,
        request_type: AIRequestTypes = AIRequestTypes.COMPLETION,
        history: str = "",
        response_format: str = "text",
    ):
        self.prompt = prompt
        self.model = model
        self.attachments = attachments
        self.set_tools(tools)
        self.chat_session_key = chat_session_key
        self.user_id = user_id
        self.temperature = temperature
        self.tool_choice = tool_choice
        self.request_type = request_type
        self.history = HISTORY.format(history=history) if history else ""
        self.response_format = response_format or "text"

        model_type = LlmModels.get_model(model)
        self.temperature_enabled = model_type.temperature_enabled

    def set_tools(self, tools: list):
        self.tool_configs = [tool.AI_CONFIG for tool in tools]
        self.tools = tools
        return self
    
    def get_tool_by_name(self, name: str):
        for tool in self.tools:
            if tool.AI_CONFIG["function"]["name"] == name:
                return tool
        raise Exception(f"Tool {name} not found")
    
    def get_tool_config_by_name(self, name: str):
        for tool in self.tool_configs:
            if tool["function"]["name"] == name:
                return tool
        raise Exception(f"Tool {name} not found")
    
    def add_tool_output(
        self, 
        tool_call: ChatCompletionMessageToolCallUnion, 
        assistent_message: dict, 
        output: str
    ):
        self.prompt.append(assistent_message)
        self.prompt.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": output,
        })
        return self

    @classmethod
    def format_prompt(cls, prompt: list[str], history: str) -> str:
        formatted_prompt = [{"role": "system", "content": history}]
        formatted_prompt.extend([
            { "role": "user" if i == len(prompt) - 1 else "system", "content": content }
            for i, content in enumerate(prompt)
        ])
        return formatted_prompt