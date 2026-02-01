from json import loads

from openai.types.chat import ChatCompletion

from modules.ai.domains.ai_response import AIResponseDomain
from modules.ai.domains.ai_request import AIRequestDomain
from modules.ai.models import AICall


class AIResponseFactory:
    def build_from_llm_response(self, ai_response: ChatCompletion, ai_request: AIRequestDomain) -> AIResponseDomain:
        content = ai_response.choices[0].message.content
        try:
            response = loads(content)
        except Exception:
            response = content
            
        return AIResponseDomain(
            total_tokens=ai_response.usage.total_tokens,
            input_used_tokens=ai_response.usage.prompt_tokens,
            output_used_tokens=ai_response.usage.completion_tokens,
            response=response,
            prompt=ai_request.prompt,
            ai_response=ai_response,
            model=ai_request.model,
            id=ai_response.id,
        )
    
    def build_from_model(self, model: AICall) -> AIResponseDomain:
        return AIResponseDomain(
            total_tokens=model.total_tokens,
            input_used_tokens=model.input_used_tokens,
            output_used_tokens=model.output_used_tokens,
            response=model.response,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            prompt=model.prompt,
            model=model.model,
            is_error=model.is_error,
        )
