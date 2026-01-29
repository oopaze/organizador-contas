from modules.ai.domains.ai_response import AIResponseDomain
from modules.ai.factories.ai_response import AIResponseFactory
from modules.ai.models import AICall


class AICallRepository:
    def __init__(self, model: AICall, ai_response_factory: AIResponseFactory):
        self.model = model
        self.ai_response_factory = ai_response_factory

    def create(self, ai_response: AIResponseDomain) -> AIResponseDomain:
        ai_call_instance = self.model.objects.create(
            prompt=ai_response.prompt,
            response=ai_response.response,
            total_tokens=ai_response.total_tokens,
            input_used_tokens=ai_response.input_used_tokens,
            output_used_tokens=ai_response.output_used_tokens,
            response_id=ai_response.google_response.response_id,
            model=ai_response.model,
        )
        return self.ai_response_factory.build_from_model(ai_call_instance)
