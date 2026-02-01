from modules.ai.domains.ai_request import AIRequestDomain, AIRequestTypes
from modules.ai.domains.ai_response import AIResponseDomain


class AIRequestFactory:
    def build(
        self, 
        prompt: list[str], 
        model: str, 
        tools: list = [],
        chat_session_key = None,
        user_id: int = None,
        temperature: float = 0.1,
        tool_choice: str = "auto",
        history: str = "",
    ) -> AIRequestDomain:
        return AIRequestDomain(
            prompt=AIRequestDomain.format_prompt(prompt, history), 
            model=model, 
            tools=tools,
            chat_session_key=chat_session_key,
            user_id=user_id,
            temperature=temperature,
            tool_choice=tool_choice,
            request_type=AIRequestTypes.COMPLETION,
            history=history,
        )
    
    def build_for_tool_request(self, prompt: list[str], ai_request: AIRequestDomain) -> AIRequestDomain:
        return AIRequestDomain(
            prompt=prompt,
            model=ai_request.model,
            chat_session_key=ai_request.chat_session_key,
            user_id=ai_request.user_id,
            temperature=ai_request.temperature,
            tools=ai_request.tools,
            tool_choice=ai_request.tool_choice,
            request_type=AIRequestTypes.TOOL_CALL,
            history=ai_request.history,
        )
    
    def build_empty_response(self, ai_request: AIRequestDomain) -> AIResponseDomain:
        return AIResponseDomain(
            total_tokens=0,
            input_used_tokens=0,
            output_used_tokens=0,
            response=AIResponseDomain.get_fallback_error_message(),
            prompt=ai_request.prompt,
            model=ai_request.model,
            is_error=True,
        )
