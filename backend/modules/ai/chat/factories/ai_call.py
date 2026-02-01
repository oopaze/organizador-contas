from modules.ai.chat.domains.ai_call import AICallDomain
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
            model=model.model,
        )
