from decimal import Decimal

from django.db.models import Count, DecimalField, Q, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from modules.loans.domains.loan import LoanDomain
from modules.loans.factories.loan import LoanFactory
from modules.loans.models import Loan


class LoanRepository:
    def __init__(self, model: Loan, loan_factory: LoanFactory):
        self.model = model
        self.factory = loan_factory

    @property
    def queryset(self):
        return (
            self.model.objects.exclude(deleted_at__isnull=False)
            .select_related("actor")
            .prefetch_related("payments")
            .order_by("-lent_at")
        )

    def get(self, loan_id: str, user_id: int, include_payments: bool = True) -> LoanDomain:
        instance = self.queryset.get(id=loan_id, user_id=user_id)
        return self.factory.build_from_model(instance, include_payments=include_payments)

    def get_all(self, user_id: int, filters: dict | None = None) -> list[LoanDomain]:
        qs = self.queryset.filter(user_id=user_id, **(filters or {}))
        return [self.factory.build_from_model(i, include_payments=True) for i in qs]

    def has_active_for_actor(self, actor_id: int, user_id: int) -> bool:
        return self.queryset.filter(
            user_id=user_id, actor_id=actor_id, status="active"
        ).exists()

    def create(self, loan: LoanDomain) -> LoanDomain:
        instance = self.model.objects.create(
            user_id=loan.user_id,
            actor_id=loan.actor_id,
            principal_amount=loan.principal_amount,
            lent_at=loan.lent_at,
            description=loan.description,
            status=loan.status,
            file_id=loan.file_id,
        )
        return self.factory.build_from_model(instance)

    def update(self, loan: LoanDomain) -> LoanDomain:
        instance = self.queryset.get(id=loan.id, user_id=loan.user_id)
        instance.actor_id = loan.actor_id
        instance.principal_amount = loan.principal_amount
        instance.lent_at = loan.lent_at
        instance.description = loan.description
        instance.status = loan.status
        instance.file_id = loan.file_id
        instance.save()
        return self.factory.build_from_model(instance, include_payments=True)

    def delete(self, loan_id: str, user_id: int):
        self.queryset.filter(id=loan_id, user_id=user_id).update(deleted_at=timezone.now())

    def stats(self, user_id: int) -> dict:
        from modules.loans.models import LoanPayment

        qs = self.model.objects.filter(user_id=user_id).exclude(deleted_at__isnull=False)

        loan_agg = qs.aggregate(
            total_lent=Coalesce(Sum("principal_amount"), Decimal("0"), output_field=DecimalField()),
            active_principal=Coalesce(
                Sum("principal_amount", filter=Q(status="active")),
                Decimal("0"), output_field=DecimalField(),
            ),
            settled_principal=Coalesce(
                Sum("principal_amount", filter=Q(status="settled")),
                Decimal("0"), output_field=DecimalField(),
            ),
            active_count=Count("id", filter=Q(status="active")),
            settled_count=Count("id", filter=Q(status="settled")),
            cancelled_count=Count("id", filter=Q(status="cancelled")),
        )

        payment_qs = LoanPayment.objects.filter(loan__user_id=user_id).exclude(deleted_at__isnull=False)
        payment_agg = payment_qs.aggregate(
            total_received=Coalesce(Sum("amount"), Decimal("0"), output_field=DecimalField()),
            payments_count=Count("id"),
        )

        return {
            "total_lent": loan_agg["total_lent"],
            "total_received": payment_agg["total_received"],
            "total_outstanding": loan_agg["total_lent"] - payment_agg["total_received"],
            "active_principal": loan_agg["active_principal"],
            "settled_principal": loan_agg["settled_principal"],
            "active_count": loan_agg["active_count"],
            "settled_count": loan_agg["settled_count"],
            "cancelled_count": loan_agg["cancelled_count"],
            "payments_count": payment_agg["payments_count"],
        }
