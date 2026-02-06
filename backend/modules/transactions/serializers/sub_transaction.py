from modules.transactions.domains import SubTransactionDomain
from modules.transactions.types import TransactionCategory
from modules.transactions.serializers import ActorSerializer

SUB_TRANSACTION_FOR_TOOL_PROMPT = """
SubTransaction {description}:
- id: {sub_transaction_id}
- Valor: {amount}
- Parcela: {installment_info}
- Ator: {actor}
- Tipo: {type}
- Categoria: {category}
"""

class SubTransactionSerializer:
    def __init__(self, actor_serializer: ActorSerializer):
        self.actor_serializer = actor_serializer

    def serialize(self, sub_transaction: "SubTransactionDomain", include_actor: bool = True) -> dict:
        return {
            "id": sub_transaction.id,
            "date": sub_transaction.date,
            "description": sub_transaction.description,
            "amount": sub_transaction.amount,
            "actor": self.actor_serializer.serialize(sub_transaction.actor) if include_actor and sub_transaction.actor else None,
            "transaction_id": sub_transaction.transaction.id,
            "transaction_identifier": sub_transaction.transaction.transaction_identifier,
            "installment_info": sub_transaction.installment_info,
            "created_at": sub_transaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": sub_transaction.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "user_provided_description": sub_transaction.user_provided_description,
            "paid_at": sub_transaction.paid_at.strftime("%Y-%m-%d %H:%M:%S") if sub_transaction.paid_at else None,
            "category": TransactionCategory.get_by_name(sub_transaction.category).value,
        }

    def serialize_many(self, sub_transactions: list["SubTransactionDomain"], include_actor: bool = True) -> list[dict]:
        return [self.serialize(sub_transaction, include_actor) for sub_transaction in sub_transactions]
    
    def serialize_for_tool(self, sub_transaction: "SubTransactionDomain") -> str:
        return SUB_TRANSACTION_FOR_TOOL_PROMPT.format(
            description=sub_transaction.description,
            sub_transaction_id=sub_transaction.id,
            amount=sub_transaction.amount,
            installment_info=sub_transaction.installment_info,
            actor=sub_transaction.actor_id if sub_transaction.actor else "Nenhum",
            type="Entrada" if sub_transaction.amount < 0 else "Saída",
            category=sub_transaction.category,
        )
    
    def serialize_many_for_tool(self, sub_transactions: list["SubTransactionDomain"]) -> str:
        return "\n".join([self.serialize_for_tool(sub_transaction) for sub_transaction in sub_transactions])
