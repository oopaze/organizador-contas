from django.db import models

from modules.base.models import SoftDeleteModel, TimedModel, UserOwnedModel


class PurchaseIntention(TimedModel, UserOwnedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planejada"
        BOUGHT = "bought", "Comprada"
        DISMISSED = "dismissed", "Descartada"

    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    transaction = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_intentions",
    )

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["month"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.amount} ({self.month})"
