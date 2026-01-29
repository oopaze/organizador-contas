from django.db import models

from modules.base.models import TimedModel, UserOwnedModel


class Conversation(TimedModel, UserOwnedModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    ai_call = models.ForeignKey("ai.AICall", on_delete=models.DO_NOTHING, null=True, blank=True)


class Message(TimedModel):
    class Role(models.TextChoices):
        HUMAN = "human", "Human"
        ASSISTANT = "assistant", "Assistant"

    role = models.CharField(max_length=255, choices=Role.choices)
    content = models.TextField()
    conversation = models.ForeignKey(Conversation, on_delete=models.DO_NOTHING)
    ai_call = models.ForeignKey("ai.AICall", on_delete=models.DO_NOTHING, null=True, blank=True)
    embedding = models.ForeignKey("ai.EmbeddingCall", on_delete=models.DO_NOTHING, null=True, blank=True)
