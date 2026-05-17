from datetime import date, datetime
from decimal import Decimal
from typing import Any

from modules.ai.mcp.domains.query_result import QueryResult


class QueryResultFactory:
    def from_cursor(
        self,
        cursor,
        *,
        started_at_ms: int,
        row_limit: int,
        now_ms: int,
    ) -> QueryResult:
        columns = [d[0] for d in cursor.description]
        raw_rows = cursor.fetchall()

        truncated = len(raw_rows) > row_limit
        if truncated:
            raw_rows = raw_rows[:row_limit]

        rows = [
            [self._serialize(cell) for cell in row]
            for row in raw_rows
        ]
        execution_ms = max(0, now_ms - started_at_ms)
        return QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            truncated=truncated,
            execution_ms=execution_ms,
        )

    def _serialize(self, value: Any) -> Any:
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        return value
