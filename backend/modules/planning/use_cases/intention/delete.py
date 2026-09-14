from modules.planning.repositories.intention import PurchaseIntentionRepository


class DeletePurchaseIntentionUseCase:
    def __init__(self, intention_repository: PurchaseIntentionRepository):
        self.intention_repository = intention_repository

    def execute(self, intention_id: int, user_id: int):
        intention = self.intention_repository.get(intention_id, user_id)
        if intention.status == "bought":
            raise ValueError("Intenção já virou transação; gerencie pelo extrato")
        self.intention_repository.delete(intention_id, user_id)
        return {"message": "success"}
