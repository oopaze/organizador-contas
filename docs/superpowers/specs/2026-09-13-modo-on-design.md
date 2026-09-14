# Modo On — lançamento no momento e conciliação de fatura — Design Spec

**Data:** 2026-09-13
**Status:** Aguardando revisão do usuário

## Objetivo

Hoje o sistema entra em lote: o usuário sobe a fatura em PDF no fim do mês e a IA cria tudo de uma vez. Esta atualização muda o **gatilho** para o momento da transação. O usuário lança na hora, pelo celular, com o mínimo de campos, e o upload da fatura passa a ser **conferência**: a IA concilia o que já foi lançado com o que a fatura diz, e o usuário confirma.

O vínculo atual é preservado integralmente: subtransação sempre pertence a uma transação, e compra no cartão continua agrupada na fatura. O balanço passa a ser único e contínuo, separando **realizado** (pago) de **previsto** (não pago + futuros).

Nenhum modelo é criado ou alterado. A estrutura atual de `Transaction` + `SubTransaction` atende; o que muda é regra de negócio, endpoints e UI.

## Decisões de design

1. **Sem mudança de schema** (decisão explícita do usuário). `Transaction` e `SubTransaction` já têm tudo: `paid_at` nos dois, `file` para distinguir fatura importada, `category`, `transaction_identifier`, `main_transaction`/`installment_number`/`recurrence_count`.
2. **Fatura em aberto por convenção.** Cada cartão/mês tem uma `Transaction` sem `file`, `category=credit_card`, `transaction_type=outgoing`, que acumula as compras como subs **não pagas**. O total é materializado a cada compra com `RecalculateAmountUseCase`.
3. **Pago/não pago no create.** O lançamento rápido decide: cartão nasce **não pago**; dinheiro/débito/pix nasce **pago**. O usuário pode marcar "previsão" (não pago, data futura) para agendados.
4. **Balanço único.** Todo lançamento entra, pago ou não. `realizado` = só pagos; `previsto` = todos; `a pagar`/`a receber` = não pagos por direção. A previsibilidade vem de **recorrências/parcelas** (já modeladas) **e** de **agendados manuais**.
5. **Conciliação por IA com confirmação.** No upload da fatura, a IA casa linha a linha. Nada muda sem o "Conciliar" do usuário. A linha da fatura vence; a sub do tempo real é soft-deleted. Anotações que a fatura não tem (`actor`, `user_provided_description`) são copiadas antes de descartar.
6. **Upload vira conferência.** A porta de entrada principal passa a ser o lançamento rápido; o dashboard ganha extrato com saldo corrente e cards de realizado/previsto.

## Contexto verificado

Fatos do código atual que sustentam a spec:

- `CreateTransactionUseCase.execute_if_not_recurrent` já cria pai + sub 1/1 (`backend/modules/transactions/use_cases/transaction/create.py:30-35`), via `SubTransactionFactory.build_from_transaction` (`factories/sub_transaction.py:44-51`).
- `SubTransaction.transaction_id` é o vínculo (`models.py:52`); `Transaction.file_id` é o marcador de fatura importada (`serializers/transaction.py:56`).
- Fatura enviada: `BillFactory.build_from_file` **não** passa `transaction_type`; cai no default `outgoing` (`file_reader/domains/bill.py:16`) — apesar do prompt pedir `"incoming"` (`upload_file.py:60`). Na prática, fatura é `outgoing`.
- Subs da fatura são criadas sem `paid_at` (`file_reader/repositories/bill_sub_transaction.py:19-26`).
- `TransactionStatsUseCase` soma o `total_amount` do pai por `transaction_type`; pago pelo `paid_at` do pai; "a receber" por subs com ator (`use_cases/transaction/stats.py:24-47`).
- `RecalculateAmountUseCase` faz `total_amount` do pai := soma das subs (`use_cases/transaction/recalculate_amount.py:9-14`).
- Filtro mensal do dashboard é `due_date__month`/`due_date__year` (`views.py:97-101`).
- Quick add hoje é só "Adicionar Receita" (`frontend/src/app/pages/dashboard-page.tsx:227`), sem pago/não pago e sem conceito de cartão.
- PWA instalável já existe (`2026-09-09-poupix-pwa-design.md`) — lançar pelo celular não exige trabalho novo de plataforma.
- Salário não cria sub (`create.py:33-34`), então existem transações sem subs no banco.

## Convenções (sem schema novo)

### Fatura em aberto

Campos que identificam uma fatura em aberto:

- `file = null`
- `category = credit_card`
- `transaction_type = outgoing`
- `transaction_identifier = "Fatura {rótulo} MM/AAAA"`, onde `{rótulo}` é o apelido do cartão (ex: `Nubank`) e `MM/AAAA` é o mês da compra (competência).
- `due_date` = dia 1 do mês da compra. Motivo: o dashboard filtra por `due_date__month/year` (`views.py:97-101`), então a fatura em aberto aparece no mês em que as compras aconteceram.

Busca/criação normaliza o rótulo (`strip`, comparação case-insensitive) para não criar duas faturas abertas do mesmo cartão.

### Regra de contagem do extrato

Vale para `LedgerUseCase` e para qualquer visão de saldo:

- Se a `Transaction` tem subs ativas → o extrato mostra **as subs**, nunca o total do pai (evita dobrar).
- Se não tem subs (ex: salário) → o extrato mostra **o próprio pai**, com `date = due_date`.
- Direção da entrada = `transaction_type` do pai. `amount` das subs é sempre positivo (regra do modelo atual).
- Data da entrada = `sub.date`; fallback `transaction.due_date`.

### Cartão no balanço

- Compra no cartão entra no extrato **na data da compra**, como não paga (previsto).
- Quando a fatura é paga (`POST /transactions/transactions/{id}/pay/` com `update_sub_transactions=true`, fluxo já existente), as subs ganham `paid_at` e migram de previsto para realizado — **sem lançar de novo**, sem dobrar.
- Isso mantém a assinatura do usuário: "todas as transações lançadas afetam a conta; só existe um balanço".

## Arquitetura

### Backend — use cases novos

Tudo dentro de `backend/modules/transactions/` (não é módulo novo: é a mesma entidade de domínio).

```
backend/modules/transactions/use_cases/transaction/
├── quick_add.py
├── ledger.py
├── reconcile_bill_preview.py
└── apply_reconciliation.py
```

Mudanças aditivas em artefatos existentes:

- `TransactionRepository.create` aceita `paid_at` no create (hoje só existe `update_paid_at`).
- `SubTransactionRepository.create` aceita `paid_at` no create.
- `TransposeFileBillToModelsUseCase.execute` passa a retornar a lista de ids das transações criadas.
- `UploadFileView.post` passa a retornar `{"message": ..., "transaction_ids": [...]}`.
- `TransactionsContainer` registra os quatro use cases novos.
- `TransactionViewSet` ganha as actions `quick_add`, `ledger`, `reconcile_preview`, `reconcile_apply`.
- `schema_docs.py` documenta a convenção da fatura em aberto (ver seção MCP).

Dependências de IA seguem o padrão de `GuessSubTransactionsCategoryUseCase`: `ask_use_case` + `ai_call_repository` injetados via `TransactionsContainer` (`container.py:207-213`).

### QuickAddTransactionUseCase

`POST /transactions/transactions/quick_add/`

Payload:

```json
{
  "direction": "outgoing",
  "payment_method": "cash",
  "amount": "54.90",
  "description": "Padaria",
  "date": "2026-09-13",
  "category": "food_grocery",
  "actor_id": 3,
  "is_paid": true,
  "card_label": "Nubank"
}
```

Regras:

- **`cash`** (dinheiro/débito/pix): cria `Transaction` com `due_date=date`, `transaction_type=direction`, `transaction_identifier=description`, `category` (ou `OTHER`), `paid_at = date` se `is_paid` senão `null`; cria sub 1/1 com `date`, `description`, `amount`, `category`, `actor_id` e o mesmo `paid_at`. Agendado = `is_paid=false` com `date` futura.
- **`credit`**: exige `card_label`. Faz `get_or_create` da fatura em aberto do mês de `date` (convenção acima). Cria a sub **não paga** e roda `RecalculateAmountUseCase` na fatura. Ignora `is_paid=true` (cartão sempre nasce não pago). `amount` entra como positivo; a direção vem do pai (`outgoing`).
- `is_salary=false`, `is_recurrent=false`. Recorrentes/parcelados continuam pelo `CreateTransactionUseCase` atual.
- Retorno:

```json
{
  "transaction": { ...TransactionSerializer... },
  "sub_transaction_id": 40,
  "open_bill_total": "320.45"
}
```

Notas:

- O vínculo se mantém: toda compra de cartão é uma `SubTransaction` apontando para a fatura em aberto.
- Categoria ausente não bloqueia: usa `OTHER`; o dialog oferece "Sugerir com IA" em cima do use case existente.
- Se o rótulo não existir, a fatura em aberto é criada com `total_amount=0` e recalculada na mesma request.

### LedgerUseCase

`GET /transactions/transactions/ledger/?start=YYYY-MM-DD&end=YYYY-MM-DD&include_unpaid=true`

Algoritmo:

1. Busca transações do usuário com `due_date` no range, com subs não deletadas.
2. Aplica a regra de contagem (subs se existirem; senão o pai).
3. Ordena por data (empate: id).
4. Acumula `running_balance += amount` se `incoming`, `-= amount` se `outgoing`.
5. Summary: `realized_balance` (só entradas com `paid_at`), `projected_balance` (todas), `payable` (outgoing não pagas), `receivable` (incoming não pagas), `incoming_total`, `outgoing_total`.

Resposta:

```json
{
  "entries": [
    {
      "date": "2026-09-13",
      "description": "Padaria",
      "amount": "54.90",
      "direction": "outgoing",
      "paid_at": null,
      "category": "food_grocery",
      "transaction_id": 12,
      "sub_transaction_id": 40,
      "transaction_identifier": "Fatura Nubank 09/2026",
      "is_card": true,
      "running_balance": "-54.90"
    }
  ],
  "summary": {
    "realized_balance": "1200.00",
    "projected_balance": "845.55",
    "payable": "354.45",
    "receivable": "0.00",
    "incoming_total": "1200.00",
    "outgoing_total": "354.45"
  }
}
```

`is_card` = `transaction.category == credit_card` (cobre fatura em aberto e fatura importada, que sempre nascem com essa categoria). `include_unpaid=false` remove entradas sem `paid_at`.

### ReconcileBillPreviewUseCase

`POST /transactions/transactions/reconcile/preview/` com `{"bill_transaction_id": 55}`.

1. Carrega a fatura (ownership, `file` não nulo, `category=credit_card`).
2. Candidatas: faturas em aberto do usuário (`file=null`, `category=credit_card`, não deletadas) com `due_date` na janela `[bill.due_date - 2 meses, bill.due_date + 1 mês]`. A janela cobre compras atrasadas, adiantadas e sobras de conciliação anterior.
3. Serializa as subs da fatura e as subs candidatas (id, data, descrição, valor, parcela, categoria).
4. Chama a IA (JSON) e valida: ids pertencem às listas, pareamento 1:1, `confidence` entre 0 e 1.
5. Retorna **sem mutação**:

```json
{
  "bill": {"id": 55, "identifier": "Nubank", "due_date": "2026-09-20"},
  "pairs": [
    {
      "bill_sub_transaction_id": 101,
      "real_sub_transaction_id": 40,
      "real_transaction_id": 12,
      "confidence": 0.94,
      "reason": "mesmo valor e data",
      "bill": {"date": "...", "description": "...", "amount": "..."},
      "real": {"date": "...", "description": "...", "amount": "..."}
    }
  ],
  "unmatched_bill": [ ...subs da fatura sem par... ],
  "unmatched_real": [ ...subs em aberto sem par... ],
  "suggested_categories": [
    {"sub_transaction_id": 101, "category": "food_grocery"}
  ]
}
```

Fatura sem nenhuma compra em tempo real → `pairs=[]`; o front mostra "nada para conciliar" e permite só aplicar categorias.

### Prompt de conciliação

```
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
{"pairs":[{"bill_sub_transaction_id":1,"real_sub_transaction_id":2,"confidence":0.0,"reason":"..."}],
 "categories":[{"sub_transaction_id":1,"category":"..."}],
 "unmatched_bill_sub_transaction_ids":[1],
 "unmatched_real_sub_transaction_ids":[2]}
```

Segue o padrão de `GuessSubTransactionsCategoryUseCase` (`guess_sub_transactions_category.py:53-73`), registrando o `AICall` para a página de insights.

### ApplyReconciliationUseCase

`POST /transactions/transactions/reconcile/apply/`

```json
{
  "pairs": [{"bill_sub_transaction_id": 101, "real_sub_transaction_id": 40}],
  "categories": [{"sub_transaction_id": 101, "category": "food_grocery"}]
}
```

1. Valida ownership e que as duas subs continuam ativas. A "real" precisa pertencer a uma fatura em aberto.
2. Para cada par: copia `actor_id` e `user_provided_description` da real para a bill sub **se a bill sub não tiver** (a fatura vence em valor, data, descrição, parcela e categoria; anotação do usuário sobrevive).
3. Soft-delete da real sub.
4. Aplica as categorias confirmadas (inclusive nas não casadas).
5. Recalcula o total de cada fatura em aberto tocada; se ficou sem subs ativas, soft-delete da fatura em aberto (mesma mecânica de `DeleteTransactionUseCase._delete_transaction`).
6. Retorna `{"merged": 1, "categorized": 1, "unmatched_remaining": 0, "closed_open_bills": [12]}`.

Compras feitas depois do fechamento não casam e **permanecem na fatura em aberto** para a próxima conciliação (a janela de candidatas as traz de volta).

O endpoint aceita pares escolhidos à mão pelo usuário, mesmo sem sugestão da IA — necessário para câmbio/divergência de valor.

### Endpoints

| Método + path | Ação |
|---|---|
| `POST /transactions/transactions/quick_add/` | Lançamento rápido (cash/credit) |
| `GET /transactions/transactions/ledger/?start&end&include_unpaid` | Extrato com saldo corrente + summary |
| `POST /transactions/transactions/reconcile/preview/` | Preview da conciliação (sem mutação) |
| `POST /transactions/transactions/reconcile/apply/` | Aplica pares/categorias confirmados |
| `POST /file_reader/upload/` (existente) | Passa a devolver `transaction_ids` das faturas criadas |

Autenticação `JWTAuthentication` nos quatro, como o resto do módulo (`views.py:84-85`).

### Frontend

**Lançamento rápido** — `quick-add-dialog.tsx`, aberto por um botão de ação fixo (FAB) visível no celular e no desktop:

- Toggle Despesa / Receita.
- Valor (`inputMode="decimal"`), Descrição, Data (default hoje, aceita futura = previsão).
- Pagamento: `Dinheiro/Débito/Pix` (nasce pago) ou `Cartão` (select de rótulos já existentes + "novo cartão"; nasce não pago; o toggle de pago some).
- Toggle "Já paguei/recebi" quando `Dinheiro/Débito/Pix` (default ligado; desligar = agendado).
- Categoria opcional com botão "Sugerir com IA"; ator opcional reusando a lista de `actors`.
- Ao salvar: `quickAddTransaction` + refresh do extrato e das stats.

**Extrato no dashboard** — nova seção/aba "Conta" no topo de `dashboard-page.tsx`:

- Lista por data com `running_balance`, chip de pago/previsto e chip de cartão.
- Filtro realizado/previsto.
- Cards existentes passam a exibir **realizado + previsto** (Saldo projetado em destaque; "Falta pagar" e "A receber" continuam).

**Conciliação** — `reconcile-bill-dialog.tsx`, aberto automaticamente quando o `uploadBill` devolve ids de fatura:

- Lista de pares com os dois lados (valor/data/descrição), confiança e checkbox (marcado por default).
- Seções de não casados da fatura e não casados do tempo real.
- Categorias sugeridas exibidas por linha, editáveis.
- Botão "Conciliar N"; rodapé com "Nada para conciliar" quando vazio.
- O fluxo antigo (upload cria e acabou) continua funcionando se a resposta não tiver ids — tolerância a contrato antigo.

**Serviços** em `frontend/src/services/transactions/`: `quickAddTransaction.ts`, `getLedger.ts`, `previewReconciliation.ts`, `applyReconciliation.ts`; `uploadBill.ts` tipado para devolver `transaction_ids` (opcional). Tipos novos em `services/types.ts`: `LedgerEntry`, `LedgerSummary`, `ReconcilePreview`, `ReconcilePair`.

`add-transaction-dialog.tsx` continua existindo para receitas/recorrentes/parceladas; o quick add é o caminho padrão.

### MCP

Sem tabela nova e sem mudança no scoper. `modules/ai/mcp/schema_docs.py`:

- `transactions_transaction`: acrescentar que `file_id IS NULL` + `category = 'credit_card'` + `transaction_type = 'outgoing'` identifica uma **fatura em aberto** acumulada em tempo real; e que o extrato conta as subs quando existem, senão o pai.
- `transactions_subtransaction`: acrescentar que compras de cartão em tempo real vivem em faturas em aberto até a conciliação com o PDF.

## Edge cases

| Caso | Comportamento |
|---|---|
| Compra depois do fechamento da fatura | Não casa; permanece na fatura em aberto e é candidata na próxima conciliação (janela de ±2 meses). |
| Usuário lançou a mesma compra duas vezes | IA casa uma; a duplicata fica em `unmatched_real` e o usuário exclui pelo extrato. |
| Compra em dólar (valor da fatura difere do digitado) | Não casa por valor; o dialog permite pareamento manual e o apply aceita pares manuais. |
| Estorno / valor negativo na fatura | Casa só com amount idêntico (sinal incluso). |
| Fatura reaplicada | Subs já soft-deleted saem das queries; preview vazio e apply idempotente. |
| Fatura em aberto fica sem subs ativas | Soft-delete automático ao final do apply. |
| Fatura sem nenhum lançamento em tempo real | `pairs=[]`; usuário aplica só categorias ou fecha. |
| Múltiplos cartões | Uma fatura aberta por rótulo; a janela inclui todas e a IA decide o pareamento. |
| Salário (transação sem sub) | O extrato mostra o pai (regra de contagem). |
| Total da fatura em aberto | Recalculado a cada compra; nunca fica somando manualmente. |
| `is_paid=true` em `payment_method=credit` | Ignorado; cartão nasce não pago. |
| Rótulo com espaços/maiúsculas | Normalizado no `get_or_create`; sem fatura aberta duplicada. |
| Fatura importada antiga (fluxo de hoje) | Continua sendo criada exatamente como hoje; a conciliação só atua quando o usuário confirma. |

## Não-objetivos

- Entidade `Account`/`Card`, qualquer migration ou campo novo.
- Open Finance / sincronização bancária.
- OCR de comprovante em imagem (já fora do PWA).
- Guardar estado/auditoria da conciliação (sem campo; aplicar é definitivo).
- Reescrever o fluxo de upload ou de planilha (`upload_sheet`).
- Recorrência automática de compras de cartão.
- Migrar os dados existentes: a convenção só afeta faturas abertas novas.

## Testes

Backend, padrão pytest do módulo (`backend/modules/transactions/tests/`):

- `test_quick_add_use_case.py`
  - cash pago: pai e sub com `paid_at`, total e direção corretos.
  - cash não pago futuro: agendado com `paid_at=null`.
  - credit: cria fatura em aberto na convenção, sub não paga, total recalculado.
  - credit na mesma fatura aberta: reusa e soma.
  - rótulo normalizado (case/trim) não duplica.
- `test_ledger_use_case.py`
  - transações com subs e sem subs (salário) sem dupla contagem.
  - `running_balance` com mistura de entradas/saídas.
  - summary realizado vs previsto; `include_unpaid=false`.
- `test_reconcile_bill_preview_use_case.py`
  - IA mockada com pares válidos, ids inválidos, pareamento 1:N e resposta malformada.
  - fatura sem candidata; candidata fora da janela.
- `test_apply_reconciliation_use_case.py`
  - soft-delete da real, cópia de `actor`/`user_provided_description`.
  - recálculo e fechamento da fatura aberta vazia.
  - par manual não sugerido pela IA.
  - reaplicação idempotente.
- Views: ownership, payload inválido, `category` de fatura errada no preview.
- `test_transpose_file_bill_to_models_use_case.py`: passa a validar os ids retornados.
- `test_upload_file_use_case.py`: `transaction_ids` na resposta.

Frontend (manual no PWA, sem suite nova):

1. Lançar débito pago e ver no extrato como realizado.
2. Lançar compra de cartão e ver o total da fatura em aberto subir.
3. Subir a fatura e ver o dialog de conciliação com os pares.
4. Desmarcar um par e aplicar; a linha do tempo real fica e a da fatura sai.
5. Pagar a fatura e ver as subs migrarem de previsto para realizado sem dobrar o saldo.

## Riscos

1. **Convenção no lugar de schema.** Rótulo de cartão errado cria fatura aberta duplicada. Mitigação: select com rótulos existentes + normalização; duplicata é visível no extrato e removível.
2. **IA erra o pareamento.** Confirmação humana obrigatória, regra de valor exato e pareamento manual disponível. Pior caso: o usuário desmarca a linha errada.
3. **`due_date` dia 1 da fatura aberta é aproximação.** Não afeta o matching (que usa as subs, não o pai); afeta só o mês em que o container aparece.
4. **Dupla contagem.** Se alguma visão somar pai e subs juntos, o saldo dobra. Mitigação: centralizar a regra no `LedgerUseCase` e reusar em qualquer visão nova.
5. **Mudança de contrato do upload.** O front tolera resposta sem `transaction_ids` para não quebrar durante deploy defasado.
6. **Perda de anotação da sub em tempo real.** Mitigada copiando `actor`/`user_provided_description` antes do soft-delete; o restante (valor/data/descrição) vem da fatura por decisão de design.

## Verificação

- `pytest backend/modules/transactions/tests backend/modules/file_reader/tests` verde.
- `yarn build` no frontend verde.
- Os cinco passos manuais da seção de testes no PWA instalado.
- `GET /transactions/transactions/ledger/` com uma fatura em aberto: compras aparecem como previsto; depois do pay da fatura, como realizado, sem linha duplicada.
