from typing import TYPE_CHECKING
from django.db.models import Case, When, Value, CharField, Exists, OuterRef

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

    @property
    def queryset(self):
        return self.model.objects.all().order_by("-created_at")

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
        ai_call_instances = self.queryset.filter(id__in=ai_call_ids).prefetch_related("conversations", "messages", "files")

        if filter_by_model:
            ai_call_instances = ai_call_instances.filter(model=filter_by_model)

        if due_date_start and due_date_end:
            ai_call_instances = ai_call_instances.filter(created_at__gte=due_date_start, created_at__lte=due_date_end)

        # Use Exists subqueries to avoid JOINs that cause duplicates
        ai_call_instances = ai_call_instances.annotate(
            related_to=Case(
                When(Exists(Conversation.objects.filter(ai_call_id=OuterRef("pk"))), then=Value("conversation")),
                When(Exists(Message.objects.filter(ai_call_id=OuterRef("pk"))), then=Value("message")),
                When(Exists(File.objects.filter(ai_call_id=OuterRef("pk"))), then=Value("file")),
                default=Value("unknown"),
                output_field=CharField(),
            )
        )

        return [self.ai_call_factory.build_from_model(ai_call) for ai_call in ai_call_instances]
