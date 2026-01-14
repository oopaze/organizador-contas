from modules.pdf_reader.domains.ai_call import AICallDomain
from modules.pdf_reader.factories.ai_call import AICallFactory
from modules.pdf_reader.models import AICall


class AICallRepository:
    def __init__(self, model: AICall, ai_call_factory: AICallFactory):
        self.model = model
        self.ai_call_factory = ai_call_factory

    def create(self, ai_call: AICallDomain) -> AICallDomain:
        ai_call_instance = self.model.objects.create(
            prompt=ai_call.prompt,
            response=ai_call.response,
            total_tokens=ai_call.total_tokens,
            input_used_tokens=ai_call.input_used_tokens,
            output_used_tokens=ai_call.output_used_tokens,
        )
        return self.ai_call_factory.build_from_model(ai_call_instance)
