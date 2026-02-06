from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from modules.ai.factories.ai_response import AIResponseFactory
    from modules.ai.domains.ai_response import AIResponseDomain
    from modules.ai.models import AICall


class AICallRepository:
    def __init__(self, model: "AICall", ai_response_factory: "AIResponseFactory"):
        self.model = model
        self.ai_response_factory = ai_response_factory

    def create(self, ai_response: "AIResponseDomain") -> "AIResponseDomain":
        ai_call_instance = self.model.objects.create(
            prompt=ai_response.prompt,
            response=ai_response.response or {},
            total_tokens=ai_response.total_tokens,
            input_used_tokens=ai_response.input_used_tokens if ai_response.input_used_tokens else 0,
            output_used_tokens=ai_response.output_used_tokens if ai_response.output_used_tokens else 0,
            response_id=ai_response.id,
            model=ai_response.model,
            is_error=ai_response.is_error,
        )
        return self.ai_response_factory.build_from_model(ai_call_instance)

    def get(self, ai_call_id: str) -> "AIResponseDomain":
        ai_call_instance = self.model.objects.get(id=ai_call_id)
        return self.ai_response_factory.build_from_model(ai_call_instance)
