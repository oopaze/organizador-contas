from json import loads

from google.genai.types import GenerateContentResponse

from modules.file_reader.domains.ai_call import AICallDomain
from modules.ai.models import AICall


class AICallFactory:
    def build_from_model(self, model: AICall) -> AICallDomain:
        return AICallDomain(
            prompt=model.prompt,
            response=model.response,
            total_tokens=model.total_tokens,
            input_used_tokens=model.input_used_tokens,
            output_used_tokens=model.output_used_tokens,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def build_from_ai_response(self, prompt, ai_response: GenerateContentResponse) -> AICallDomain:
        return AICallDomain(
            prompt=prompt,
            response=loads(ai_response.text),
            total_tokens=ai_response.usage_metadata.total_token_count,
            input_used_tokens=ai_response.usage_metadata.prompt_token_count,
            output_used_tokens=ai_response.usage_metadata.candidates_token_count,
        )
