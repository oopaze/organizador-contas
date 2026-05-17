from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QueryResult:
    """Result of an `execute_sql` call, ready to be serialized to MCP."""

    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    truncated: bool
    execution_ms: int

    def to_dict(self) -> dict:
        return {
            "columns": self.columns,
            "rows": self.rows,
            "row_count": self.row_count,
            "truncated": self.truncated,
            "execution_ms": self.execution_ms,
        }
