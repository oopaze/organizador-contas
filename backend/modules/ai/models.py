from django.db import models

from modules.base.models import TimedModel


class AICall(TimedModel):
    prompt = models.JSONField()
    response = models.JSONField()

    response_id = models.CharField(max_length=100, null=True, blank=True)

    total_tokens = models.IntegerField()

    input_used_tokens = models.IntegerField()
    output_used_tokens = models.IntegerField()

    def __str__(self):
        return f"AICall {self.id} - {self.total_tokens} tokens"
    
    def __repr__(self):
        return f"<AICall {self.id} - {self.total_tokens} tokens>"
