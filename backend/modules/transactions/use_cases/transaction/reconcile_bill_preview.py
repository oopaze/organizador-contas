from datetime import timedelta
from typing import TYPE_CHECKING

from modules.transactions.repositories import SubTransactionRepository, TransactionRepository
from modules.transactions.types import TransactionCategory

if TYPE_CHECKING:
    from modules.ai.repositories.ai_call import AICallRepository
    from modules.ai.use_cases.ask import AskUseCase


RECONCILE_PROMPT = """
Você é um conciliador de faturas de cartão de crédito. Recebe duas listas:
- FATURA: linhas oficiais da fatura recém-enviada.
- TEMPO_REAL: compras lançadas pelo usuário no app antes da fatura chegar.

Case cada linha de FATURA com no máximo uma linha de TEMPO_REAL.

REGRAS:
1. O valor deve bater exatamente (centavos). Sinal diferente não casa.
2. Prefira datas iguais; aceite diferença de até 5 dias.
3. Descrições podem divergir (apelido do usuário vs nome na fatura) — use similaridade.
4. Considere installment_info (ex: 3/12) quando existir.
5. Nunca invente ids; use apenas ids das listas.
6. Na dúvida, não case: deixe em unmatched.
7. Atribua categoria apenas para linhas da FATURA sem categoria ou em "other".

CATEGORIAS PERMITIDAS: {categories}

FATURA:
{bill_sub_transactions}

TEMPO_REAL:
{real_sub_transactions}

OUTPUT (JSON apenas):
{{"pairs":[{{"bill_sub_transaction_id":1,"real_sub_transaction_id":2,"confidence":0.0,"reason":"..."}}],
 "categories":[{{"sub_transaction_id":1,"category":"..."}}],
 "unmatched_bill_sub_transaction_ids":[1],
 "unmatched_real_sub_transaction_ids":[2]}}
"""


class ReconcileBillPreviewUseCase:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        sub_transaction_repository: SubTransactionRepository,
        ai_call_repository: "AICallRepository",
        ask_use_case: "AskUseCase",
    ):
        self.transaction_repository = transaction_repository
        self.sub_transaction_repository = sub_transaction_repository
        self.ai_call_repository = ai_call_repository
        self.ask_use_case = ask_use_case

    def execute(self, bill_transaction_id: int, user_id: int) -> dict:
        bill = self.transaction_repository.get(bill_transaction_id, user_id)
        if bill.file_id is None or bill.category != TransactionCategory.CREDIT_CARD.name:
            raise ValueError("A transação informada não é uma fatura de cartão importada")

        candidates = self.transaction_repository.get_open_bills(
            user_id,
            due_date_start=bill.due_date - timedelta(days=62),
            due_date_end=bill.due_date + timedelta(days=31),
        )
        bill_card_id = getattr(bill, "card_id", None)
        if bill_card_id is not None:
            candidates = [
                candidate for candidate in candidates
                if getattr(candidate, "card_id", None) == bill_card_id
            ]
        bill_subs = self.sub_transaction_repository.get_all_by_transaction_id(bill.id, user_id)
        candidate_ids = [candidate.id for candidate in candidates]
        real_subs = self.sub_transaction_repository.get_all_by_transaction_ids(candidate_ids)
        if not bill_subs or not real_subs:
            return self._empty_preview(bill, bill_subs)

        ai_response = self._ask_ai(bill_subs, real_subs, user_id)
        pairs, categories = self._validate(ai_response, bill_subs, real_subs)

        paired_bill_ids = {pair["bill_sub_transaction_id"] for pair in pairs}
        paired_real_ids = {pair["real_sub_transaction_id"] for pair in pairs}
        return {
            "bill": {"id": bill.id, "identifier": bill.transaction_identifier, "due_date": bill.due_date.isoformat()},
            "pairs": [
                {
                    **pair,
                    "bill": self._sub_payload(next(s for s in bill_subs if s.id == pair["bill_sub_transaction_id"])),
                    "real": self._sub_payload(next(s for s in real_subs if s.id == pair["real_sub_transaction_id"])),
                }
                for pair in pairs
            ],
            "unmatched_bill": [self._sub_payload(s) for s in bill_subs if s.id not in paired_bill_ids],
            "unmatched_real": [self._sub_payload(s) for s in real_subs if s.id not in paired_real_ids],
            "suggested_categories": categories,
        }

    def _ask_ai(self, bill_subs, real_subs, user_id) -> dict:
        prompt = RECONCILE_PROMPT.format(
            categories=[category.name for category in TransactionCategory.get_all()],
            bill_sub_transactions=self._serialize_for_prompt(bill_subs),
            real_sub_transactions=self._serialize_for_prompt(real_subs),
        )
        ai_call_id = self.ask_use_case.execute([prompt], user_id, response_format="json_object")
        response = self.ai_call_repository.get(ai_call_id).response
        if isinstance(response, list):
            response = response[0] if response else {}
        return response if isinstance(response, dict) else {}

    def _validate(self, response: dict, bill_subs, real_subs) -> tuple[list, list]:
        bill_ids = {sub.id for sub in bill_subs}
        real_ids = {sub.id for sub in real_subs}
        pairs = []
        used_bill_ids = set()
        used_real_ids = set()
        for pair in response.get("pairs", []):
            bill_sub_id = pair.get("bill_sub_transaction_id")
            real_sub_id = pair.get("real_sub_transaction_id")
            if bill_sub_id not in bill_ids or real_sub_id not in real_ids:
                continue
            if bill_sub_id in used_bill_ids or real_sub_id in used_real_ids:
                continue
            used_bill_ids.add(bill_sub_id)
            used_real_ids.add(real_sub_id)
            pairs.append(
                {
                    "bill_sub_transaction_id": bill_sub_id,
                    "real_sub_transaction_id": real_sub_id,
                    "real_transaction_id": next(s for s in real_subs if s.id == real_sub_id).transaction.id,
                    "confidence": pair.get("confidence", 0),
                    "reason": pair.get("reason", ""),
                }
            )
        categories = [
            {"sub_transaction_id": item["sub_transaction_id"], "category": item["category"]}
            for item in response.get("categories", [])
            if item.get("sub_transaction_id") in bill_ids and item.get("category")
        ]
        return pairs, categories

    def _empty_preview(self, bill, bill_subs) -> dict:
        return {
            "bill": {"id": bill.id, "identifier": bill.transaction_identifier, "due_date": bill.due_date.isoformat()},
            "pairs": [],
            "unmatched_bill": [self._sub_payload(s) for s in bill_subs],
            "unmatched_real": [],
            "suggested_categories": [],
        }

    def _serialize_for_prompt(self, subs) -> str:
        return "\n".join(
            f"- id: {sub.id} | data: {sub.date} | descrição: {sub.description} | "
            f"valor: {sub.amount} | parcela: {sub.installment_info or '-'} | categoria: {sub.category}"
            for sub in subs
        )

    def _sub_payload(self, sub) -> dict:
        return {
            "id": sub.id,
            "date": sub.date.isoformat(),
            "description": sub.description,
            "amount": str(sub.amount),
            "installment_info": sub.installment_info,
            "category": sub.category,
        }
