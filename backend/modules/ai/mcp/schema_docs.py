"""Human-readable descriptions for the tables exposed via MCP.

Update this file when adding or removing a scoped table. The
`describe_schema` tool merges these descriptions with introspected
column metadata from `Model._meta`.
"""


TABLE_DESCRIPTIONS = {
    "transactions_transaction": (
        "Transação principal — uma conta, um pagamento, uma fatura, ou um "
        "salário. Linhas soft-deleted (deleted_at IS NOT NULL) já são "
        "filtradas automaticamente."
    ),
    "transactions_subtransaction": (
        "Itens individuais que compõem uma transação principal "
        "(ex: linhas de uma fatura de cartão). Sempre ligados a uma "
        "transactions_transaction via transaction_id."
    ),
    "transactions_actor": (
        "Pessoa ou entidade envolvida em uma sub-transação (ex: alguém "
        "que dividiu uma conta com você). Opcional."
    ),
    "file_reader_file": (
        "Arquivo original (PDF/Excel) de onde uma transação foi extraída "
        "por IA."
    ),
    "loans_loan": (
        "Empréstimo feito pelo usuário a um Actor. principal_amount é o valor "
        "original; saldo restante = principal_amount - SUM(loans_loanpayment.amount). "
        "status: active/settled/cancelled. file_id aponta opcionalmente para o "
        "comprovante de origem."
    ),
    "loans_loanpayment": (
        "Pagamento recebido de um empréstimo. Ligado a loans_loan via loan_id. "
        "file_id aponta para o comprovante PIX do pagamento, quando enviado."
    ),
}


COLUMN_NOTES = {
    ("transactions_transaction", "main_transaction_id"):
        "Definido em parcelas (installments); null no parent.",
    ("transactions_transaction", "is_salary"):
        "True quando a transação representa um recebimento de salário.",
    ("transactions_subtransaction", "transaction_id"):
        "FK para a transação principal que contém este item.",
}


# Tables exposed via describe_schema and protected by the CTE scoper.
SCOPED_TABLES = [
    "transactions_transaction",
    "transactions_subtransaction",
    "transactions_actor",
    "file_reader_file",
    "loans_loan",
    "loans_loanpayment",
]
