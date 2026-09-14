from modules.planning.domains.intention import PurchaseIntentionDomain
from modules.planning.models import PurchaseIntention


class PurchaseIntentionFactory:
    def build_from_model(self, model: PurchaseIntention) -> PurchaseIntentionDomain:
        return PurchaseIntentionDomain(
            id=model.id,
            name=model.name,
            amount=model.amount,
            month=model.month,
            installments=model.installments,
            status=model.status,
            transaction_id=model.transaction_id,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    def build(self, data: dict) -> PurchaseIntentionDomain:
        return PurchaseIntentionDomain(
            name=data["name"],
            amount=data["amount"],
            month=data["month"],
            installments=data.get("installments", 1),
            status=data.get("status", "planned"),
            transaction_id=data.get("transaction_id"),
            user_id=data["user_id"],
        )
