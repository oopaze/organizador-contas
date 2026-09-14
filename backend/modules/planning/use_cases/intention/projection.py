from datetime import date, datetime
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

from django.core.exceptions import ObjectDoesNotExist
from dateutil.relativedelta import relativedelta

from modules.planning.domains.intention import PurchaseIntentionDomain
from modules.planning.repositories.intention import PurchaseIntentionRepository
from modules.userdata.repositories.profile import ProfileRepository


class ProjectionUseCase:
    """Monthly outlook: guaranteed salary minus real spending minus planned installments.

    Expenses are the user's average monthly outgoing over the last 3 months
    of transactions. Each planned intention contributes its monthly
    installment value to every month between its first month and the end of
    its installment plan — including intentions started in previous months.
    """

    EXPENSE_WINDOW_MONTHS = 3

    def __init__(
        self,
        intention_repository: PurchaseIntentionRepository,
        profile_repository: ProfileRepository,
        sub_transaction_repository,
    ):
        self.intention_repository = intention_repository
        self.profile_repository = profile_repository
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, user_id: int, start: str = None, end: str = None, months: int = 12) -> dict:
        start_date = self._parse_month(start) if start else date.today().replace(day=1)
        end_date = self._parse_month(end) if end else start_date + relativedelta(months=months - 1)

        planned = self.intention_repository.filter(
            {"user_id": user_id, "status": "planned", "month__gte": start_date}
        )
        salary = self._salary(user_id)
        expenses = self._average_monthly_expenses(user_id)

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
                    "expenses": self._money(expenses),
                    "intentions_total": self._money(commitments),
                    "leftover": self._money(salary - expenses - commitments),
                }
            )
            current += relativedelta(months=1)

        # Fetch and include goals
        try:
            profile = self.profile_repository.get_by_user_id(user_id)
        except ObjectDoesNotExist:
            profile = None
        
        goals = {
            "monthly_spending_goal": str(profile.monthly_spending_goal) if profile and profile.monthly_spending_goal else None,
            "monthly_savings_goal": str(profile.monthly_savings_goal) if profile and profile.monthly_savings_goal else None,
            "monthly_essentials_goal": str(profile.monthly_essentials_goal) if profile and profile.monthly_essentials_goal else None,
        }

        return {"months": projection, "total_months": len(projection), "goals": goals}

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

    def _average_monthly_expenses(self, user_id: int) -> Decimal:
        today = date.today()
        window_start = today.replace(day=1) - relativedelta(months=self.EXPENSE_WINDOW_MONTHS)
        try:
            subs = self.sub_transaction_repository.get_by_date_range(
                user_id, window_start.isoformat(), today.isoformat()
            )
        except Exception:
            return Decimal("0")

        monthly_totals: dict[str, Decimal] = {}
        for sub in subs:
            transaction = getattr(sub, "transaction", None)
            if transaction is None or transaction.transaction_type != "outgoing":
                continue
            month_key = str(sub.date)[:7]
            monthly_totals[month_key] = monthly_totals.get(month_key, Decimal("0")) + Decimal(str(sub.amount))

        if not monthly_totals:
            return Decimal("0")
        total = sum(monthly_totals.values(), Decimal("0"))
        return (total / len(monthly_totals)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _parse_month(self, value: str) -> date:
        try:
            parsed = datetime.strptime(str(value), "%Y-%m")
        except (TypeError, ValueError):
            raise ValueError("month deve estar no formato YYYY-MM")
        return date(parsed.year, parsed.month, 1)

    def _money(self, value) -> str:
        return f"{Decimal(value):.2f}"
