import calendar
from datetime import date

from modules.planning.repositories.intention import PurchaseIntentionRepository
from modules.planning.serializers.intention import PurchaseIntentionSerializer


class ListPurchaseIntentionsUseCase:
    def __init__(
        self,
        intention_repository: PurchaseIntentionRepository,
        intention_serializer: PurchaseIntentionSerializer,
    ):
        self.intention_repository = intention_repository
        self.intention_serializer = intention_serializer

    def execute(
        self, user_id: int, month: str = None, start: str = None, end: str = None, status: str = None
    ) -> list[dict]:
        filters = {"user_id": user_id}
        if month:
            filters["month__lte"] = self._last_day_of(month)
            if start:
                filters["month__gte"] = self._first_day_of(start)
        elif end:
            filters["month__lte"] = self._last_day_of(end)
        if status:
            filters["status"] = status

        intentions = self.intention_repository.filter(filters)
        serialized = [self.intention_serializer.serialize(intention) for intention in intentions]

        if month:
            return self._filter_by_month(intentions, serialized, month)
        if not start:
            return serialized
        return self._filter_by_range(intentions, serialized, start)

    def _filter_by_month(self, intentions: list, serialized: list, month: str) -> list:
        target = self._parse_month(month)
        result = []
        for intention, data in zip(intentions, serialized):
            intention_month = self._parse_month(intention.month)
            if intention_month == target:
                result.append(data)
            elif self._carries_over(intention, intention_month, target):
                data["carry_over"] = True
                result.append(data)
        return result

    def _filter_by_range(self, intentions: list, serialized: list, start: str) -> list:
        range_start = self._parse_month(start)
        result = []
        for intention, data in zip(intentions, serialized):
            intention_month = self._parse_month(intention.month)
            if intention_month >= range_start:
                result.append(data)
            elif self._carries_over(intention, intention_month, range_start):
                data["carry_over"] = True
                result.append(data)
        return result

    def _carries_over(self, intention, intention_month: date, target: date) -> bool:
        return (
            intention.status == "planned"
            and intention_month < target
            and self._month_offset(intention_month, target) < max(1, int(intention.installments or 1))
        )

    def _first_day_of(self, value: str) -> str:
        year, month = self._parse_month(value).year, self._parse_month(value).month
        return date(year, month, 1).isoformat()

    def _last_day_of(self, value: str) -> str:
        parsed = self._parse_month(value)
        return date(
            parsed.year, parsed.month, calendar.monthrange(parsed.year, parsed.month)[1]
        ).isoformat()

    def _parse_month(self, value) -> date:
        if isinstance(value, date):
            return date(value.year, value.month, 1)
        parsed = value.isoformat()[:7] if hasattr(value, "isoformat") else str(value)
        year, month = int(parsed[:4]), int(parsed[5:7])
        return date(year, month, 1)

    def _month_offset(self, from_month: date, to_month: date) -> int:
        return (to_month.year - from_month.year) * 12 + (to_month.month - from_month.month)
