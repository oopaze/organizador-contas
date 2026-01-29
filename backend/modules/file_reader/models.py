from django.db import models

from modules.base.models import TimedModel


class File(TimedModel):
    raw_file = models.FileField("Link to File", upload_to="files/")
    raw_text = models.TextField(null=True, blank=True)

    ai_call = models.ForeignKey("ai.AICall", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.raw_file.name

    def __repr__(self):
        return f"<File {self.id} - {self.raw_file.name}>"
