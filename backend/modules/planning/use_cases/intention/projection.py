from datetime import date, datetime
from decimal import ROUND_DOWN, Decimal

from django.core.exceptions import ObjectDoesNotExist
from dateutil.relativedelta import relativedelta

from modules.planning.domains.intention import PurchaseIntentionDomain
from modules.planning.repositories.intention import PurchaseIntentionRepository
from modules.userdata.repositories.profile import ProfileRepository


class ProjectionUseCase:
    """Monthly outlook: guaranteed salary minus planned installment commitments.

    Each planned intention contributes its monthly installment value to
    every month between its first month and the end of its installment plan.
    """

    def __init__(
        self,
        intention_repository: PurchaseIntentionRepository,
        profile_repository: ProfileRepository,
    ):
        self.intention_repository = intention_repository
        self.profile_repository = profile_repository

    def execute(self, user_id: int, start: str = None, end: str = None, months: int = 12) -> dict:
        start_date = self._parse_month(start) if start else date.today().replace(day=1)
        end_date = self._parse_month(end) if end else start_date + relativedelta(months=months - 1)

        planned = self.intention_repository.filter({"user_id": user_id, "status": "planned"})
        salary = self._salary(user_id)

        projection = []
        current = start_date
        while current <= end_date:
            commitments = sum(
                (self._installment_value(intention, current) for intention in planned),
                Decimal("0"),
            )
            projection.append(
                {
                    "month": f"{current.year:04d}-{current.month:02d}",
                    "salary": self._money(salary),
                    "intentions_total": self._money(commitments),
                    "leftover": self._money(salary - commitments),
                }
            )
            current += relativedelta(months=1)

        return {"months": projection, "total_months": len(projection)}

    def _installment_value(self, intention: "PurchaseIntentionDomain", month_date: date) -> Decimal:
        intention_month = self._parse_month(intention.month.isoformat()[:7])
        offset = (month_date.year - intention_month.year) * 12 + (month_date.month - intention_month.month)
        installments = max(1, int(intention.installments or 1))
        if offset < 0 or offset >= installments:
            return Decimal("0")

        total = Decimal(str(intention.amount))
        base = (total / installments).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        if offset == installments - 1:
            return total - base * (installments - 1)
        return base

    def _salary(self, user_id: int) -> Decimal:
        try:
            profile = self.profile_repository.get_by_user_id(user_id)
        except ObjectDoesNotExist:
            return Decimal("0")
        try:
            return Decimal(str(profile.salary or 0))
        except Exception:
            return Decimal("0")

    def _parse_month(self, value: str) -> date:
        try:
            parsed = datetime.strptime(str(value), "%Y-%m")
        except (TypeError, ValueError):
            raise ValueError("month deve estar no formato YYYY-MM")
        return date(parsed.year, parsed.month, 1)

    def _money(self, value) -> str:
        return f"{Decimal(value):.2f}"
