from datetime import date

from modules.ai.mcp.exceptions import InvalidDateError


def parse_month(value: str) -> tuple[int, int]:
    try:
        year, month = str(value).split("-")
        year, month = int(year), int(month)
    except (ValueError, AttributeError):
        raise InvalidDateError(f"mês inválido: {value!r}. Use YYYY-MM (ex.: 2026-10).")
    if not 1 <= month <= 12:
        raise InvalidDateError(f"mês inválido: {value!r}. Use YYYY-MM (ex.: 2026-10).")
    return year, month


def validate_date(value: str, field: str) -> str:
    try:
        return date.fromisoformat(str(value)).isoformat()
    except ValueError:
        raise InvalidDateError(
            f"{field} inválida: {value!r}. Use YYYY-MM-DD (ex.: 2026-10-01)."
        )
