from modules.ai.repositories.ai_call import AICallRepository
from modules.ai.serializers.ai_call import AICallSerializer


class ListAICallsUseCase:
    def __init__(self, ai_call_repository: AICallRepository, ai_call_serializer: AICallSerializer):
        self.ai_call_repository = ai_call_repository
        self.ai_call_serializer = ai_call_serializer

    def execute(self, user_id: int, filter_by_model: str = None, due_date_start: str = None, due_date_end: str = None) -> list[dict]:
        ai_calls = self.ai_call_repository.get_all_by_user_id(user_id, filter_by_model, due_date_start, due_date_end)
        return [self.ai_call_serializer.serialize(ai_call) for ai_call in ai_calls]
