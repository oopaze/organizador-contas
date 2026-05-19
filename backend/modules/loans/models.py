from django.db import models

from modules.base.models import TimedModel, UserOwnedModel, SoftDeleteModel


class Loan(TimedModel, UserOwnedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Ativo"
        SETTLED = "settled", "Quitado"
        CANCELLED = "cancelled", "Cancelado"

    actor = models.ForeignKey(
        "transactions.Actor",
        on_delete=models.PROTECT,
        related_name="loans",
    )
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    lent_at = models.DateField()
    description = models.CharField(max_length=255, blank=True, default="")
    file = models.ForeignKey(
        "file_reader.File",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="origin_loans",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        ordering = ["-lent_at"]
        indexes = [
            models.Index(fields=["actor"]),
            models.Index(fields=["status"]),
            models.Index(fields=["lent_at"]),
        ]

    def __str__(self):
        return f"Loan {self.id} to actor {self.actor_id} R${self.principal_amount}"


class LoanPayment(TimedModel, SoftDeleteModel):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateField()
    note = models.CharField(max_length=255, blank=True, default="")
    file = models.ForeignKey(
        "file_reader.File",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loan_payments",
    )

    class Meta:
        ordering = ["-paid_at"]
        indexes = [
            models.Index(fields=["loan", "paid_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["file"],
                condition=models.Q(deleted_at__isnull=True, file__isnull=False),
                name="unique_active_file_per_loan_payment",
            ),
        ]

    def __str__(self):
        return f"LoanPayment {self.id} for loan {self.loan_id} R${self.amount}"
