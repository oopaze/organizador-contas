from collections import defaultdict
from decimal import Decimal


class LedgerUseCase:
    def __init__(self, transaction_repository, sub_transaction_repository):
        self.transaction_repository = transaction_repository
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, user_id: int, start=None, end=None, include_unpaid: bool = True) -> dict:
        filters = {"user_id": user_id}
        if start:
            filters["due_date__gte"] = start
        if end:
            filters["due_date__lte"] = end
        transactions = self.transaction_repository.filter(filters)
        transaction_ids = [transaction.id for transaction in transactions]

        all_subs = self.sub_transaction_repository.get_all_by_transaction_ids(transaction_ids)
        subs_count_by_transaction = defaultdict(int)
        for sub in all_subs:
            subs_count_by_transaction[sub.transaction.id] += 1

        entries = []
        parent_only_ids = [
            transaction.id for transaction in transactions
            if subs_count_by_transaction[transaction.id] == 0
        ]
        for transaction in transactions:
            if transaction.id in parent_only_ids:
                entries.append(
                    self._build_entry(
                        transaction=transaction,
                        sub=None,
                        date=transaction.due_date,
                        description=transaction.transaction_identifier,
                        amount=transaction.total_amount,
                        paid_at=transaction.paid_at,
                        category=transaction.category,
                    )
                )

        period_subs = self.sub_transaction_repository.get_by_date_range(user_id, start, end) if start and end else all_subs
        for sub in period_subs:
            if sub.transaction.id in parent_only_ids:
                continue
            entries.append(
                self._build_entry(
                    transaction=sub.transaction,
                    sub=sub,
                    date=sub.date,
                    description=sub.description,
                    amount=sub.amount,
                    paid_at=sub.paid_at,
                    category=sub.category,
                )
            )

        entries = [self._normalize_entry(entry) for entry in entries]
        entries.sort(key=lambda entry: (entry["date"], entry["transaction_id"], entry["sub_transaction_id"] or 0))

        running_balance = Decimal("0")
        for entry in entries:
            amount = Decimal(entry["amount"])
            running_balance += amount if entry["direction"] == "incoming" else -amount
            entry["running_balance"] = self._money(running_balance)

        if not include_unpaid:
            entries = [entry for entry in entries if entry["paid_at"]]

        return {"entries": entries, "summary": self._summary(entries)}

    def _build_entry(self, transaction, sub, date, description, amount, paid_at, category) -> dict:
        return {
            "date": date,
            "description": description,
            "amount": amount,
            "direction": transaction.transaction_type,
            "paid_at": paid_at,
            "category": category,
            "transaction_id": transaction.id,
            "sub_transaction_id": sub.id if sub else None,
            "transaction_identifier": transaction.transaction_identifier,
            "is_card": transaction.category == "credit_card",
        }

    def _normalize_entry(self, entry: dict) -> dict:
        return {
            **entry,
            "date": self._iso(entry["date"]),
            "paid_at": self._iso(entry["paid_at"]),
            "amount": self._money(entry["amount"]),
        }

    def _iso(self, value):
        if value is None:
            return None
        return value.isoformat() if hasattr(value, "isoformat") else value

    def _summary(self, entries: list) -> dict:
        realized = Decimal("0")
        projected = Decimal("0")
        payable = Decimal("0")
        receivable = Decimal("0")
        incoming_total = Decimal("0")
        outgoing_total = Decimal("0")
        for entry in entries:
            amount = Decimal(entry["amount"])
            signed = amount if entry["direction"] == "incoming" else -amount
            projected += signed
            if entry["direction"] == "incoming":
                incoming_total += amount
            else:
                outgoing_total += amount
            if entry["paid_at"]:
                realized += signed
            elif entry["direction"] == "outgoing":
                payable += amount
            else:
                receivable += amount
        return {
            "realized_balance": self._money(realized),
            "projected_balance": self._money(projected),
            "payable": self._money(payable),
            "receivable": self._money(receivable),
            "incoming_total": self._money(incoming_total),
            "outgoing_total": self._money(outgoing_total),
        }

    def _money(self, value) -> str:
        return f"{Decimal(value):.2f}"
