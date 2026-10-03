from decimal import Decimal

from modules.cards.repositories import CardRepository
from modules.transactions.repositories import SubTransactionRepository, TransactionRepository
from modules.transactions.types import TransactionCategory


class SummarizeSpendingUseCase:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        sub_transaction_repository: SubTransactionRepository,
        card_repository: CardRepository,
    ):
        self.transaction_repository = transaction_repository
        self.sub_transaction_repository = sub_transaction_repository
        self.card_repository = card_repository

    def execute(self, user_id: int, filters: dict = {}) -> dict:
        transaction_type = filters.get("transaction_type") or "outgoing"
        group_by = filters.get("group_by") or "none"
        due_filters = {key: value for key, value in filters.items() if key.startswith("due_date__")}
        purchase_filters = {key: value for key, value in filters.items() if key.startswith("purchase_")}
        category = filters.get("category")
        search = (filters.get("search") or "").strip().lower()

        transactions = self.transaction_repository.filter(
            {"user_id": user_id, "transaction_type": transaction_type, **due_filters}
        )
        sub_transactions = self.sub_transaction_repository.get_all_by_transaction_ids(
            [transaction.id for transaction in transactions]
        )
        subs_by_transaction: dict[int, list] = {}
        for sub_transaction in sub_transactions:
            subs_by_transaction.setdefault(sub_transaction.transaction.id, []).append(sub_transaction)

        cards = {card.id: card.name for card in self.card_repository.get_all(user_id)}

        items = []
        for transaction in transactions:
            transaction_subs = subs_by_transaction.get(transaction.id, [])
            if transaction_subs:
                for sub_transaction in transaction_subs:
                    if category and sub_transaction.category != category:
                        continue
                    if search and search not in (sub_transaction.description or "").lower():
                        continue
                    if not self._in_purchase_window(sub_transaction.date, purchase_filters):
                        continue
                    items.append({
                        "category": sub_transaction.category,
                        "card_id": transaction.card_id,
                        "date": sub_transaction.date,
                        "amount": Decimal(str(sub_transaction.amount)),
                    })
            else:
                if category and transaction.category != category:
                    continue
                if search and search not in (transaction.transaction_identifier or "").lower():
                    continue
                if not self._in_purchase_window(transaction.due_date, purchase_filters):
                    continue
                items.append({
                    "category": transaction.category,
                    "card_id": transaction.card_id,
                    "date": transaction.due_date,
                    "amount": Decimal(str(transaction.total_amount)),
                })

        total = sum((item["amount"] for item in items), Decimal("0"))
        return {
            "total": self._money(total),
            "count": len(items),
            "currency": "BRL",
            "groups": self._build_groups(items, group_by, cards),
        }

    def _in_purchase_window(self, value, filters: dict) -> bool:
        if not filters:
            return True
        value_str = str(value)
        if filters.get("purchase_month") and value_str[:7] != filters["purchase_month"]:
            return False
        if filters.get("purchase_start") and value_str < filters["purchase_start"]:
            return False
        if filters.get("purchase_end") and value_str > filters["purchase_end"]:
            return False
        return True

    def _build_groups(self, items: list[dict], group_by: str, cards: dict) -> list[dict]:
        if group_by == "none":
            return []
        buckets: dict = {}
        for item in items:
            if group_by == "category":
                key = item["category"] or TransactionCategory.OTHER.name
                label = getattr(TransactionCategory.get_by_name(key), "value", TransactionCategory.OTHER.value)
            elif group_by == "card":
                key = str(item["card_id"]) if item["card_id"] else "sem_cartao"
                label = cards.get(item["card_id"], "Sem cartão") if item["card_id"] else "Sem cartão"
            else:  # month
                key = str(item["date"])[:7]
                label = key
            bucket = buckets.setdefault(
                key, {"key": key, "label": label, "total": Decimal("0"), "count": 0}
            )
            bucket["total"] += item["amount"]
            bucket["count"] += 1
        groups = [
            {"key": bucket["key"], "label": bucket["label"], "total": self._money(bucket["total"]), "count": bucket["count"]}
            for bucket in buckets.values()
        ]
        return sorted(groups, key=lambda group: Decimal(group["total"]), reverse=True)

    @staticmethod
    def _money(value: Decimal) -> str:
        return str(value.quantize(Decimal("0.01")))
