from django.db import models

from modules.base.models import SoftDeleteModel, TimedModel, UserOwnedModel


class Card(TimedModel, UserOwnedModel, SoftDeleteModel):
    name = models.CharField(max_length=255)
    due_day = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
