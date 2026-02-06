from typing import TYPE_CHECKING

from modules.transactions.models import SubTransaction
from modules.transactions.types import TransactionCategory
from modules.transactions.repositories import SubTransactionRepository
from modules.transactions.serializers import SubTransactionSerializer
from modules.ai.prompts import BOT_DESCRIPTION, MODELS_EXPLANATION_PROMPT

if TYPE_CHECKING:
    from modules.ai.repositories.ai_call import AICallRepository
    from modules.ai.use_cases.ask import AskUseCase

PROMPT = """
Você é um Especialista em Classificação de Dados Financeiros.
Sua tarefa é analisar descrições de subtransações e atribuir a categoria mais precisa a cada uma.

### 📋 LISTA DE CATEGORIAS PERMITIDAS:
{categories}

### 🕹️ REGRAS DE OURO:
1. Analise o campo 'description' de cada subtransação para decidir a categoria.
2. Se o valor for NEGATIVO, considere que pode ser um 'Estorno' ou 'Reembolso', mas mantenha a categoria original do gasto (ex: estorno de restaurante continua em 'Alimentação').
3. Se houver nomes de pessoas (Actors) vinculados, foque na descrição da transação, não no nome da pessoa.
4. Se uma descrição for ambígua, use 'Outros'.
5. RETORNE APENAS O JSON. Proibido explicações, markdown ou texto adicional.

### 📥 INPUT (Subtransactions):
{sub_transactions}

### 📤 OUTPUT FORMAT:
[
    {{
        "sub_transaction_id": "string ou int",
        "category": "string"
    }}
]
"""


class GuessSubTransactionsCategoryUseCase:
    def __init__(
        self, 
        sub_transaction_repository: SubTransactionRepository,
        sub_transaction_serializer: SubTransactionSerializer,
        ai_call_repository: "AICallRepository",
        ask_use_case: "AskUseCase",
    ):
        self.sub_transaction_repository = sub_transaction_repository
        self.sub_transaction_serializer = sub_transaction_serializer
        self.ai_call_repository = ai_call_repository
        self.ask_use_case = ask_use_case

    def execute(self, transaction_id: int, user_id: int):
        sub_transactions = self.sub_transaction_repository.get_all_by_transaction_id(transaction_id, user_id)
        sub_transactions_for_tool = self.sub_transaction_serializer.serialize_many_for_tool(sub_transactions)
        categories = [category.name for category in TransactionCategory.get_all()]
        prompt = PROMPT.format(sub_transactions=sub_transactions_for_tool, categories=categories)
        ai_call_id = self.ask_use_case.execute([BOT_DESCRIPTION, MODELS_EXPLANATION_PROMPT, prompt], user_id, response_format="json_object")
        ai_call = self.ai_call_repository.get(ai_call_id)

        updated_sub_transactions = []
        for sub_transaction in ai_call.response:
            try:
                sub_transaction_instance = self.sub_transaction_repository.get(sub_transaction["sub_transaction_id"], user_id)
                sub_transaction_instance.category = sub_transaction["category"]
                self.sub_transaction_repository.update(sub_transaction_instance)
                updated_sub_transactions.append(sub_transaction_instance)
            except SubTransaction.DoesNotExist:
                continue

        return {
            "message": f"{len(updated_sub_transactions)} sub transações atualizadas com sucesso",
        }

        
