# Loans — Design Spec

**Data:** 2026-05-19
**Status:** Aprovado pelo usuário — pronto para writing-plans

## Objetivo

Permitir ao usuário registrar empréstimos que ele fez para pessoas (Actors), rastrear pagamentos recebidos, ver saldo devedor, e subir comprovantes PIX em PDF que a IA parseia automaticamente para criar o registro de pagamento já vinculado ao arquivo.

Os dados também devem ser consultáveis via servidor MCP existente, permitindo perguntas como "quanto Amor ainda me deve?" diretamente em um cliente MCP.

## Decisões de design

1. **Modelo dedicado, sem reuso de `Transaction`** — empréstimo tem semântica distinta (principal fixo, pagamentos parciais e indefinidos no tempo). Forçar dentro de Transaction misturaria conceitos e quebraria invariantes existentes.
2. **Loan obrigatório no upload** — o usuário escolhe o Loan no modal; a IA não tenta adivinhar. Simplifica UX e elimina ambiguidade.
3. **Sem categoria** — Loan é uma entidade própria, não precisa entrar na taxonomia de despesas.
4. **Sem espelho em Transaction** — Loans tem seu próprio dashboard. Se no futuro for útil ver pagamentos no fluxo mensal, agrega-se via view dedicada.
5. **Só PDF no MVP** — espelha o `UploadBillDialog` atual. Imagens (JPG/PNG) podem ser adicionadas depois.
6. **MCP via SQL existente** — adiciona as novas tabelas ao scoper read-only; não introduz tool MCP nova.

## Arquitetura

### Novo módulo `backend/modules/loans/`

Estrutura espelhando `modules/transactions/`:

```
modules/loans/
├── __init__.py
├── admin.py
├── apps.py
├── container.py
├── domains/
│   ├── __init__.py
│   ├── loan.py
│   └── loan_payment.py
├── factories/
│   ├── __init__.py
│   ├── loan.py
│   └── loan_payment.py
├── migrations/
│   └── 0001_initial.py
├── models.py
├── repositories/
│   ├── __init__.py
│   ├── loan.py
│   └── loan_payment.py
├── serializers/
│   ├── __init__.py
│   ├── loan.py
│   └── loan_payment.py
├── tests/
│   ├── domains/
│   ├── repositories/
│   ├── use_cases/
│   └── views/
├── urls.py
├── use_cases/
│   ├── __init__.py
│   ├── loan/
│   │   ├── create_loan.py
│   │   ├── delete_loan.py
│   │   ├── get_loan.py
│   │   ├── list_loans.py
│   │   ├── loan_stats.py
│   │   └── update_loan.py
│   ├── loan_payment/
│   │   ├── create_loan_payment.py
│   │   ├── delete_loan_payment.py
│   │   ├── get_loan_payment.py
│   │   ├── list_loan_payments.py
│   │   ├── update_loan_payment.py
│   │   └── upload_pix_receipt.py
│   └── parse_pix_receipt.py
└── views.py
```

### Modelos

```python
# modules/loans/models.py
from django.db import models
from modules.base.models import TimedModel, UserOwnedModel, SoftDeleteModel


class Loan(TimedModel, UserOwnedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Ativo"
        SETTLED = "settled", "Quitado"
        CANCELLED = "cancelled", "Cancelado"

    actor = models.ForeignKey(
        "transactions.Actor",
        on_delete=models.PROTECT,
        related_name="loans",
    )
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    lent_at = models.DateField()
    description = models.CharField(max_length=255, blank=True, default="")
    file = models.ForeignKey(
        "file_reader.File",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="origin_loans",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        ordering = ["-lent_at"]
        indexes = [
            models.Index(fields=["actor"]),
            models.Index(fields=["status"]),
            models.Index(fields=["lent_at"]),
        ]


class LoanPayment(TimedModel, SoftDeleteModel):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateField()
    note = models.CharField(max_length=255, blank=True, default="")
    file = models.ForeignKey(
        "file_reader.File",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="loan_payments",
    )

    class Meta:
        ordering = ["-paid_at"]
        indexes = [
            models.Index(fields=["loan", "paid_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["file"],
                condition=models.Q(deleted_at__isnull=True, file__isnull=False),
                name="unique_active_file_per_loan_payment",
            ),
        ]
```

### Domain (LoanDomain)

```python
class LoanDomain:
    # ... atributos básicos ...

    @property
    def total_paid(self) -> Decimal:
        return sum((p.amount for p in self.payments or []), Decimal("0"))

    @property
    def remaining(self) -> Decimal:
        return self.principal_amount - self.total_paid

    @property
    def progress_pct(self) -> float:
        if self.principal_amount == 0:
            return 0.0
        return float(min(self.total_paid / self.principal_amount, 1) * 100)

    @property
    def is_settled(self) -> bool:
        return self.remaining <= 0
```

`CreateLoanPaymentUseCase` (e `UploadPixReceiptUseCase`) recalcula `Loan.status`: se `remaining <= 0` no commit, atualiza para `settled`; ao deletar payment, se `remaining > 0`, volta para `active`.

### API REST

Dois ViewSets registrados como rotas-irmãs em `modules/loans/urls.py` via `DefaultRouter` (mesmo padrão de `transactions`/`sub_transactions`):

```python
router.register(r"loans", LoanViewSet, basename="loans")
router.register(r"loan_payments", LoanPaymentViewSet, basename="loan_payments")
```

Incluído em `infra/urls.py` com `path("loans/", include("modules.loans.urls"))` — mesmo padrão de `transactions/` e `file_reader/` (sem prefixo `/api/`).

| Método + path | Ação |
|---|---|
| `GET /loans/loans/` | Lista loans do usuário. Filtros: `actor_id`, `status`. |
| `POST /loans/loans/` | Cria loan. Payload: `actor_id`, `principal_amount`, `lent_at`, `description?`, `file_id?`. |
| `GET /loans/loans/{id}/` | Detalhe + payments + computed (`total_paid`, `remaining`, `progress_pct`). |
| `PATCH /loans/loans/{id}/` | Edita campos editáveis. |
| `DELETE /loans/loans/{id}/` | Soft delete (cascateia em payments). |
| `GET /loans/loans/stats/` | `{total_lent, total_received, total_outstanding, by_status}`. |
| `GET /loans/loan_payments/` | Lista pagamentos. Filtros: `loan_id`, `paid_at__month`, `paid_at__year`. |
| `POST /loans/loan_payments/` | Cria pagamento manual. |
| `PATCH /loans/loan_payments/{id}/` | Edita. |
| `DELETE /loans/loan_payments/{id}/` | Soft delete. |
| `POST /loans/loan_payments/upload_receipt/` | Multipart: `file`, `loan_id` (obrigatório), `model`, `password?`. |

Autenticação via `JWTAuthentication` (mesmo padrão dos outros módulos).

### Upload de comprovante PIX

Fluxo do endpoint `POST /loans/loan_payments/upload_receipt/`:

1. Valida `loan_id` pertence ao usuário, `loan.status == active`, arquivo presente.
2. `FileFactory` + `FileRepository` salvam o arquivo (reusa infraestrutura de `file_reader`).
3. Se PDF protegido, `RemovePDFPasswordUseCase` aplica a senha.
4. `extract_text_from_pdf` extrai o texto.
5. `ParsePixReceiptUseCase` (orquestra `AskUseCase` com o prompt PIX e modelo escolhido) retorna o JSON estruturado.
6. `CreateLoanPaymentUseCase` cria o `LoanPayment` com `amount`, `paid_at`, `note=<transaction_id>`, `file=<file_id>`.
7. Recalcula status do Loan.
8. Retorna o payment serializado + `extracted_data` (campos brutos da IA pro front mostrar resumo).

**Tratamento de erro:**
- IA retorna `amount=null` ou parsing falha → response 422 `{"error": "...", "file_id": <id>}`. Front mostra dialog manual com `file_id` pré-preenchido.
- Senha inválida → 400 `{"error": "Senha inválida para o PDF"}` (mesmo wording do `UploadFileView`).
- Loan inativo → 400 `{"error": "Empréstimo já está quitado ou cancelado"}`.

### Prompt PIX

```
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
{"amount": 1000.00, "paid_at": "YYYY-MM-DD", "payer_name": "...", "payee_name": "...", "transaction_id": "...", "bank": "..."}
```

## Frontend

### Página `loans-page.tsx`

Rota: `/loans`. Item de menu "Empréstimos" no `layout.tsx`.

Componentes:
- **Stat cards no topo (padrão `dashboard-page`)** — grid responsivo `grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6`. Cada card: título pequeno + ícone à direita, número grande colorido, linha secundária em texto muted:
  1. **Emprestado** (ícone `Wallet`) — `R$ {total_lent}` / `R$ {active_principal} ativos`.
  2. **Recebido** (ícone `TrendingUp` verde) — `R$ {total_received}` (verde) / `{payments_count} pagamentos`.
  3. **A Receber** (ícone `Clock` laranja) — `R$ {total_outstanding}` (laranja) / `{active_count} empréstimos pendentes`.
  4. **Quitados** (ícone `CheckCircle2` verde) — `R$ {settled_principal}` (verde) / `{settled_count} empréstimos quitados`.
- Tabela colapsável (estilo `actors-page`) — uma linha por Loan:
  - Actor, principal, pago, falta, progresso (barra), último pagamento, ações (✏️ 🗑️ 📎).
  - Expansão mostra `LoanPaymentsTable` com data, valor, nota, link pro comprovante (download).
- Botões topo: `+ Novo empréstimo`, `Subir comprovante PIX`.

A payload de `GET /loans/loans/stats/` precisa expor:
```json
{
  "total_lent": "10000.00",
  "total_received": "1500.00",
  "total_outstanding": "8500.00",
  "active_principal": "5000.00",
  "settled_principal": "5000.00",
  "active_count": 1,
  "settled_count": 1,
  "cancelled_count": 0,
  "payments_count": 3
}
```

### Dialogs novos

- **`add-loan-dialog.tsx`** — Actor (select), principal, lent_at, descrição, upload opcional de comprovante de origem.
- **`edit-loan-dialog.tsx`** — mesmos campos, com `status`.
- **`upload-pix-receipt-dialog.tsx`** — espelho do `UploadBillDialog`:
  - Drag & drop PDF
  - Select **Loan** (obrigatório; mostra "Actor — R$X emprestados, R$Y faltam")
  - Select modelo de IA (mesmas opções do upload-bill)
  - Checkbox "PDF tem senha?" + campo senha
  - Submit → sucesso: toast + fecha + refresh; erro de parsing: dialog manual com `file_id`.
- **`add-loan-payment-dialog.tsx`** — fallback quando IA falha. Loan, amount, paid_at, note, file_id opcional.

### Serviços

Em `frontend/src/services/loans/`:
`getLoans`, `getLoan`, `createLoan`, `updateLoan`, `deleteLoan`, `getLoanStats`, `getLoanPayments`, `createLoanPayment`, `updateLoanPayment`, `deleteLoanPayment`, `uploadPixReceipt`.

## MCP

Adiciona Loans ao servidor MCP existente em `modules/ai/mcp/`. Sem tool nova — `execute_sql` já cobre.

**`services/query_scoper.py`:** estende `SCOPED_TABLES_CTE`:

```sql
loans_loan AS (
    SELECT * FROM public.loans_loan
    WHERE user_id = (SELECT id FROM me) AND deleted_at IS NULL
),
loans_loanpayment AS (
    SELECT p.* FROM public.loans_loanpayment p
    JOIN public.loans_loan l ON p.loan_id = l.id
    WHERE l.user_id = (SELECT id FROM me) AND p.deleted_at IS NULL
),
```

**`schema_docs.py`:**
- `loans_loan`: "Empréstimo feito pelo usuário a um Actor. principal_amount é o valor original; saldo restante = principal - SUM(loans_loanpayment.amount). Status: active/settled/cancelled."
- `loans_loanpayment`: "Pagamento recebido referente a um empréstimo. Ligado a loans_loan via loan_id. Pode ter file_id apontando pro comprovante PIX."

`SCOPED_TABLES` ganha `"loans_loan"` e `"loans_loanpayment"`.

## Edge cases

| Caso | Comportamento |
|---|---|
| Over-payment (paga mais que o principal) | Permitido. Status → `settled`. UI mostra "Pago a mais R$X" em cinza. |
| Editar `principal_amount` com pagamentos existentes | Permitido. Recalcula `remaining` e status. |
| Mesmo `File` em 2 pagamentos | Bloqueado por `UniqueConstraint` no LoanPayment. |
| Deletar Actor com Loans ativos | Bloqueado por `on_delete=PROTECT`. Erro claro no serializer. |
| Soft delete de Loan | Cascateia em payments (mesmo padrão Transaction/SubTransaction). |
| IA não extrai `amount` | 422 + `file_id` no payload. Front abre dialog manual. |
| PDF com senha inválida | 400 com wording padrão. |
| Loan inativo no upload | 400 explicando. |

## Migrations & deploy

- `loans/migrations/0001_initial.py` — cria `Loan` e `LoanPayment`.
- `infra/settings.py`: `INSTALLED_APPS += ["modules.loans"]`.
- `infra/urls.py`: `path("loans/", include("modules.loans.urls"))`.
- Sem migration em `transactions/` ou `file_reader/`.

## Testes

Padrão pytest dos outros módulos:

- **Domain** (`tests/domains/test_loan.py`): cálculo de `total_paid`, `remaining`, `progress_pct`; transição automática `active → settled`.
- **Use cases:**
  - `test_create_loan.py`, `test_update_loan.py`, `test_list_loans.py`, `test_loan_stats.py`
  - `test_create_loan_payment.py` — incluindo recálculo de status
  - `test_delete_loan_payment.py` — reverter status se aplicável
  - `test_parse_pix_receipt.py` — mock IA com response válido, ausente, malformado
  - `test_upload_pix_receipt.py` — integração: file save + parse + payment create + status update
- **Views** (`tests/views/`): permissões, ownership, multipart upload, erros 400/422.
- **MCP** (smoke em `modules/ai/mcp/tests/`): `execute_sql SELECT * FROM loans_loan` retorna só linhas do user; tentativa de query em outro user falha por escopo CTE.

## Não-objetivos (fora do MVP)

- Suporte a comprovantes em imagem (JPG/PNG).
- Cálculo de juros, multa, atraso.
- Inferência automática de qual Loan o comprovante pertence.
- Espelho de pagamentos como Transaction no fluxo de caixa mensal.
- Notificações de pagamentos atrasados.
- Suporte a empréstimos recebidos (apenas concedidos).
