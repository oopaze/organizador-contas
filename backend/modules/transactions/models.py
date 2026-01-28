from django.db import models

from modules.base.models import TimedModel, UserOwnedModel


class Actor(TimedModel, UserOwnedModel):
    name = models.CharField(max_length=255)


class Transaction(TimedModel, UserOwnedModel):
    class TransactionType(models.TextChoices):
        INCOMING = "incoming", "Incoming"
        OUTGOING = "outgoing", "Outgoing"

    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_identifier = models.CharField(max_length=255)
    file = models.ForeignKey("pdf_reader.File", on_delete=models.CASCADE, null=True, blank=True)
    transaction_type = models.CharField(max_length=255, choices=TransactionType.choices, default=TransactionType.OUTGOING)
    is_salary = models.BooleanField(default=False)
    is_recurrent = models.BooleanField(default=False)
    recurrence_count = models.IntegerField(null=True, blank=True)
    installment_number = models.IntegerField(null=True, blank=True)
    main_transaction = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_identifier} - {self.due_date}"
    
    def __repr__(self):
        return f"<Transaction {self.id} - {self.transaction_identifier} - {self.due_date}>"


class SubTransaction(TimedModel):
    date = models.DateField()
    description = models.CharField(max_length=255)
    user_provided_description = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    installment_info = models.CharField(max_length=255)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.date} - {self.description} - {self.amount}"
    
    def __repr__(self):
        return f"<SubTransaction {self.id} - {self.date} - {self.description} - {self.amount}>"
    