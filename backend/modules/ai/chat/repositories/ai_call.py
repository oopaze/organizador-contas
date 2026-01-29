from modules.ai.chat.domains import AICallDomain
from modules.ai.chat.factories import AICallFactory
from modules.ai.models import AICall


class AICallRepository:
    def __init__(self, model: AICall, ai_call_factory: AICallFactory):
        self.model = model
        self.ai_call_factory = ai_call_factory

    def get(self, ai_call_id: str) -> AICallDomain:
        ai_call_instance = self.model.objects.get(id=ai_call_id)
        return self.ai_call_factory.build_from_model(ai_call_instance)
