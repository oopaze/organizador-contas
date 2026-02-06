from typing import TYPE_CHECKING

from modules.ai.chat.models import Conversation, Message
from modules.file_reader.models import File


if TYPE_CHECKING:
    from modules.ai.factories.ai_response import AIResponseFactory
    from modules.ai.factories.ai_call import AICallFactory
    from modules.ai.domains.ai_response import AIResponseDomain
    from modules.ai.models import AICall


class AICallRepository:
    def __init__(self, model: "AICall", ai_response_factory: "AIResponseFactory", ai_call_factory: "AICallFactory"):
        self.model = model
        self.ai_response_factory = ai_response_factory
        self.ai_call_factory = ai_call_factory

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
    
    def get_all_by_user_id(self, user_id: int, filter_by_model: str = None, due_date_start: str = None, due_date_end: str = None) -> list:
        conversations_from_user = Conversation.objects.filter(user_id=user_id, ai_call__isnull=False).values_list("ai_call_id", flat=True)
        messages_from_user = Message.objects.filter(conversation__user_id=user_id, ai_call__isnull=False).values_list("ai_call_id", flat=True)
        files_from_user = File.objects.filter(user_id=user_id, ai_call__isnull=False).values_list("ai_call_id", flat=True)

        ai_call_ids = set(list(conversations_from_user) + list(messages_from_user) + list(files_from_user))
        ai_call_instances = self.model.objects.filter(id__in=ai_call_ids)
        
        if filter_by_model:
            ai_call_instances = ai_call_instances.filter(model=filter_by_model)

        if due_date_start and due_date_end:
            ai_call_instances = ai_call_instances.filter(created_at__gte=due_date_start, created_at__lte=due_date_end)

        return [self.ai_call_factory.build_from_model(ai_call) for ai_call in ai_call_instances]
