from django.utils import timezone

from modules.loans.domains.loan_payment import LoanPaymentDomain
from modules.loans.factories.loan_payment import LoanPaymentFactory
from modules.loans.models import LoanPayment


class LoanPaymentRepository:
    def __init__(self, model: LoanPayment, loan_payment_factory: LoanPaymentFactory):
        self.model = model
        self.factory = loan_payment_factory

    @property
    def queryset(self):
        return self.model.objects.exclude(deleted_at__isnull=False).order_by("-paid_at")

    def get(self, payment_id: str, user_id: int) -> LoanPaymentDomain:
        instance = self.queryset.get(id=payment_id, loan__user_id=user_id)
        return self.factory.build_from_model(instance)

    def get_all(self, user_id: int, filters: dict | None = None) -> list[LoanPaymentDomain]:
        qs = self.queryset.filter(loan__user_id=user_id, **(filters or {}))
        return [self.factory.build_from_model(i) for i in qs]

    def get_by_loan(self, loan_id: int) -> list[LoanPaymentDomain]:
        qs = self.queryset.filter(loan_id=loan_id)
        return [self.factory.build_from_model(i) for i in qs]

    def create(self, payment: LoanPaymentDomain) -> LoanPaymentDomain:
        instance = self.model.objects.create(
            loan_id=payment.loan_id,
            amount=payment.amount,
            paid_at=payment.paid_at,
            note=payment.note,
            file_id=payment.file_id,
        )
        return self.factory.build_from_model(instance)

    def update(self, payment: LoanPaymentDomain) -> LoanPaymentDomain:
        instance = self.queryset.get(id=payment.id)
        instance.amount = payment.amount
        instance.paid_at = payment.paid_at
        instance.note = payment.note
        instance.file_id = payment.file_id
        instance.save()
        return self.factory.build_from_model(instance)

    def delete(self, payment_id: str):
        self.queryset.filter(id=payment_id).update(deleted_at=timezone.now())
