from decimal import Decimal, InvalidOperation

from modules.transactions.models import SubTransaction
from modules.file_reader.domains.bill import BillDomain
from modules.file_reader.domains.bill_sub_transaction import BillSubTransactionDomain
from modules.file_reader.domains.file import FileDomain

PREVIOUS_INVOICE_PAYMENT_KEYWORDS = (
    "pagamento",
    "pagto",
    "pago",
    "recebido",
    "obrigado",
    "baixa",
)
LEGITIMATE_CREDIT_KEYWORDS = (
    "estorno",
    "crédito",
    "credito",
    "cancelamento",
    "devolução",
    "devolucao",
    "antecipado",
)


def is_previous_invoice_payment(transaction: dict) -> bool:
    """Detects a previous-invoice payment line printed on the bill.

    The extraction prompt asks the model to ignore those lines, but small models
    still emit them (e.g. "Baixa Pagamento Fatura Via Pix", "PAGAMENTO RECEBIDO -
    OBRIGADO"); summing them would drive the bill total negative.
    """
    try:
        amount = Decimal(str(transaction.get("amount", 0)))
    except (InvalidOperation, ValueError):
        return False
    if amount >= 0:
        return False
    description = (transaction.get("description") or "").lower()
    if any(keyword in description for keyword in LEGITIMATE_CREDIT_KEYWORDS):
        return False
    return any(keyword in description for keyword in PREVIOUS_INVOICE_PAYMENT_KEYWORDS)


class BillSubTransactionFactory:
    def build_many_from_file(self, file: FileDomain, bill: BillDomain, ai_response: dict = None) -> list[BillSubTransactionDomain]:
        if ai_response is None:
            ai_response = file.ai_call.response
        transactions = [
            transaction
            for transaction in ai_response.get("transactions", [])
            if not is_previous_invoice_payment(transaction)
        ]
        return [
            BillSubTransactionDomain(
                date=transaction["date"],
                description=transaction["description"],
                amount=transaction["amount"],
                installment_info=transaction.get("installment_info", "not installment"),
                bill=bill,
                category=transaction.get("category", bill.category),
            )
            for transaction in transactions
        ]

    def build_from_model(self, model: SubTransaction) -> BillSubTransactionDomain:
        return BillSubTransactionDomain(
            date=model.date,
            description=model.description,
            amount=model.amount,
            installment_info=model.installment_info,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            bill=model.transaction,
            category=model.category,
        )
