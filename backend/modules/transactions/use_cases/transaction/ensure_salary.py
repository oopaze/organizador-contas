import calendar
from datetime import date
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ObjectDoesNotExist

from modules.transactions.factories import TransactionFactory
from modules.transactions.repositories import TransactionRepository
from modules.transactions.serializers import TransactionSerializer
from modules.transactions.types import TransactionCategory
from modules.userdata.repositories.profile import ProfileRepository


class EnsureMonthlySalaryUseCase:
    """Guarantees the monthly salary transaction exists and is up to date.

    Past/current months are created as already received; future months as
    projected. Already-paid salaries are never touched; unpaid ones sync to
    the configured value. Idempotent: one salary per month.
    """

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        transaction_factory: TransactionFactory,
        transaction_serializer: TransactionSerializer,
        profile_repository: ProfileRepository,
    ):
        self.transaction_repository = transaction_repository
        self.transaction_factory = transaction_factory
        self.transaction_serializer = transaction_serializer
        self.profile_repository = profile_repository

    def execute(self, user_id: int, month: str) -> dict:
        try:
            profile = self.profile_repository.get_by_user_id(user_id)
        except ObjectDoesNotExist:
            return {"salary": None}

        try:
            salary_amount = Decimal(str(profile.salary))
        except (InvalidOperation, TypeError):
            return {"salary": None}
        if salary_amount <= 0:
            return {"salary": None}

        year, month_number = self._parse_month(month)
        day = min(int(profile.salary_day or 1), calendar.monthrange(year, month_number)[1])
        due_date = date(year, month_number, day).isoformat()
        identifier = f"Salário {month_number:02d}/{year}"

        existing = self.transaction_repository.filter(
            {
                "user_id": user_id,
                "is_salary": True,
                "due_date__year": year,
                "due_date__month": month_number,
            }
        )
        if existing:
            salary = existing[0]
            if salary.paid_at is None and Decimal(str(salary.total_amount)) != salary_amount:
                salary.update_amount(salary_amount)
                salary = self.transaction_repository.update(salary)
            return {"salary": self.transaction_serializer.serialize(salary)}

        if self.transaction_repository.exists_including_deleted(
            user_id=user_id,
            is_salary=True,
            due_date__year=year,
            due_date__month=month_number,
        ):
            return {"salary": None}

        today = date.today()
        paid_at = due_date if (year, month_number) <= (today.year, today.month) else None
        transaction = self.transaction_factory.build(
            {
                "due_date": due_date,
                "total_amount": salary_amount,
                "transaction_identifier": identifier,
                "transaction_type": "incoming",
                "is_salary": True,
                "user_id": user_id,
                "is_recurrent": False,
                "category": TransactionCategory.INCOME.name,
                "paid_at": paid_at,
            }
        )
        created = self.transaction_repository.create(transaction)
        return {"salary": self.transaction_serializer.serialize(created)}

    def _parse_month(self, month: str) -> tuple[int, int]:
        try:
            year, month_number = str(month).split("-")
            year, month_number = int(year), int(month_number)
        except (TypeError, ValueError):
            raise ValueError("month deve estar no formato YYYY-MM")
        if month_number < 1 or month_number > 12:
            raise ValueError("month deve estar no formato YYYY-MM")
        return year, month_number
