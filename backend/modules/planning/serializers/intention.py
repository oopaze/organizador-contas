from modules.planning.domains.intention import PurchaseIntentionDomain


class PurchaseIntentionSerializer:
    def serialize(self, intention: "PurchaseIntentionDomain") -> dict:
        return {
            "id": intention.id,
            "name": intention.name,
            "amount": str(intention.amount),
            "month": intention.month.isoformat() if hasattr(intention.month, "isoformat") else intention.month,
            "status": intention.status,
            "transaction_id": intention.transaction_id,
            "created_at": intention.created_at.strftime("%Y-%m-%d %H:%M:%S") if intention.created_at else None,
            "updated_at": intention.updated_at.strftime("%Y-%m-%d %H:%M:%S") if intention.updated_at else None,
        }
