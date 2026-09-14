from typing import TYPE_CHECKING

from modules.transactions.types import TransactionCategory

if TYPE_CHECKING:
    from modules.ai.repositories.ai_call import AICallRepository
    from modules.ai.use_cases.ask import AskUseCase


INFER_CATEGORY_PROMPT = """
Você classifica lançamentos financeiros em uma única categoria da taxonomia.

CATEGORIAS PERMITIDAS: {categories}

LANÇAMENTO: {description}

REGRAS:
1. Escolha a categoria mais específica possível.
2. Na dúvida, use "other".
3. Responda apenas JSON: {{"category": "<nome>"}}
"""


class InferTransactionCategoryUseCase:
    def __init__(self, ai_call_repository: "AICallRepository", ask_use_case: "AskUseCase"):
        self.ai_call_repository = ai_call_repository
        self.ask_use_case = ask_use_case

    def execute(self, description: str, user_id: int) -> str:
        if not description or not description.strip():
            return TransactionCategory.OTHER.name

        prompt = INFER_CATEGORY_PROMPT.format(
            categories=[category.name for category in TransactionCategory.get_all()],
            description=description.strip(),
        )
        ai_call_id = self.ask_use_case.execute([prompt], user_id, response_format="json_object")
        response = self.ai_call_repository.get(ai_call_id).response
        if isinstance(response, list):
            response = response[0] if response else {}
        if not isinstance(response, dict):
            return TransactionCategory.OTHER.name

        category = response.get("category")
        if not category or not TransactionCategory.get_by_name(category):
            return TransactionCategory.OTHER.name
        return category
