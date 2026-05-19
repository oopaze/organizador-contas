from datetime import datetime
from decimal import Decimal, InvalidOperation

from modules.ai.use_cases.ask import AskUseCase
from modules.file_reader.repositories.ai_call import AICallRepository


PROMPT = """
Aja como extrator de dados de comprovante PIX. Você recebe NOME e TEXTO de um comprovante de transferência PIX.

Extraia:
- amount (número positivo, decimal)
- paid_at (YYYY-MM-DD; data da transação, não data de emissão)
- payer_name (quem PAGOU / origem)
- payee_name (quem RECEBEU / destino)
- transaction_id (E2E ou ID interno do banco; null se não encontrar)
- bank (instituição da origem)

REGRAS:
- amount sempre positivo
- se múltiplas datas, prefira "Data do pagamento" / "Data da transação"
- vírgula decimal brasileira (R$ 1.234,56) → 1234.56
- campos não encontrados → null

FORMATO (JSON apenas):
{{"amount": 1000.00, "paid_at": "YYYY-MM-DD", "payer_name": "...", "payee_name": "...", "transaction_id": "...", "bank": "..."}}

DADOS:
- FILE NAME: {file_name}
- PDF TEXT: {pdf_text}
"""


class ParsePixReceiptUseCase:
    def __init__(self, ask_use_case: AskUseCase, ai_call_repository: AICallRepository):
        self.ask_use_case = ask_use_case
        self.ai_call_repository = ai_call_repository

    def execute(self, raw_text: str, file_name: str, user_id: int, model: str) -> dict:
        prompt = [PROMPT.format(file_name=file_name, pdf_text=raw_text)]
        ai_call_id = self.ask_use_case.execute(
            prompt, user_id, response_format="json_object", model=model
        )
        ai_call = self.ai_call_repository.get(ai_call_id)
        payload = ai_call.response or {}

        amount_raw = payload.get("amount")
        paid_at_raw = payload.get("paid_at")
        if amount_raw is None:
            raise ValueError("amount não encontrado no comprovante")
        if not paid_at_raw:
            raise ValueError("paid_at não encontrado no comprovante")

        try:
            amount = Decimal(str(amount_raw))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("amount inválido no comprovante") from exc

        try:
            paid_at = datetime.strptime(paid_at_raw, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("paid_at inválido no comprovante") from exc

        return {
            "amount": amount,
            "paid_at": paid_at,
            "payer_name": payload.get("payer_name"),
            "payee_name": payload.get("payee_name"),
            "transaction_id": payload.get("transaction_id"),
            "bank": payload.get("bank"),
            "ai_call_id": ai_call_id,
        }
