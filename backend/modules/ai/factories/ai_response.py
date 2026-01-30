from json import loads

from google.genai.types import GenerateContentResponse

from modules.ai.domains.ai_response import AIResponseDomain
from modules.ai.models import AICall


class AIResponseFactory:
    def build_from_llm_response(self, ai_response: GenerateContentResponse, prompt: list[str], model: str) -> AIResponseDomain:
        try:
            response = loads(ai_response.text)
        except Exception as e:
            response = {"text": ai_response.text}
            
        return AIResponseDomain(
            total_tokens=ai_response.usage_metadata.total_token_count,
            input_used_tokens=ai_response.usage_metadata.prompt_token_count,
            output_used_tokens=ai_response.usage_metadata.candidates_token_count,
            response=response,
            prompt=prompt,
            google_response=ai_response,
            model=model,
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
        )
