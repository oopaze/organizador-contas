from django.db import models

from modules.base.models import TimedModel


class File(TimedModel):
    raw_file = models.FileField("Link to File", upload_to="files/")
    raw_text = models.TextField(null=True, blank=True)

    ai_call = models.ForeignKey("pdf_reader.AICall", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.raw_file.name

    def __repr__(self):
        return f"<File {self.id} - {self.raw_file.name}>"


class AICall(TimedModel):
    prompt = models.JSONField()
    response = models.JSONField()

    total_tokens = models.IntegerField()

    input_used_tokens = models.IntegerField()
    output_used_tokens = models.IntegerField()

    def __str__(self):
        return f"AICall {self.id} - {self.total_tokens} tokens"
    
    def __repr__(self):
        return f"<AICall {self.id} - {self.total_tokens} tokens>"
