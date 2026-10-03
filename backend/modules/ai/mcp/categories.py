from modules.ai.mcp.exceptions import InvalidCategoryError
from modules.transactions.types import TransactionCategory


def _find_category(value: str):
    return TransactionCategory.get_by_name(value) or TransactionCategory.get_by_attribute_value(value, "value")


def resolve_category(value: str | None) -> str | None:
    if value is None:
        return None
    item = _find_category(str(value).strip())
    if item is None:
        raise InvalidCategoryError(
            f"categoria inválida: {value!r}. Use list_enums para ver os slugs válidos "
            "(ex.: transport_fuel)."
        )
    return item.name


def with_category_slug(data: dict) -> dict:
    label = data.get("category")
    item = TransactionCategory.get_by_attribute_value(label, "value") if label else None
    data["category_slug"] = item.name if item else None
    return data


def enrich_transaction(data: dict) -> dict:
    with_category_slug(data)
    for sub_transaction in data.get("sub_transactions") or []:
        with_category_slug(sub_transaction)
    return data
