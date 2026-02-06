from django.db import models

from modules.base.models import TimedModel
from pgvector.django import VectorField


class AICall(TimedModel):
    prompt = models.JSONField()
    response = models.JSONField()
    model = models.CharField(max_length=255)

    response_id = models.CharField(max_length=100, null=True, blank=True)

    total_tokens = models.IntegerField()

    input_used_tokens = models.IntegerField()
    output_used_tokens = models.IntegerField()

    is_error = models.BooleanField(default=False)
    user = models.ForeignKey("userdata.User", on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"AICall {self.id} - {self.total_tokens} tokens"
    
    def __repr__(self):
        return f"<AICall {self.id} - {self.total_tokens} tokens>"


class EmbeddingCall(TimedModel):
    embedding = VectorField(dimensions=1536)
    model = models.CharField(max_length=255)
    
    total_tokens = models.IntegerField()
    prompt_used_tokens = models.IntegerField()

    def __str__(self):
        return f"EmbeddingCall {self.id} - {self.model}"
    
    def __repr__(self):
        return f"<EmbeddingCall {self.id} - {self.model}>"