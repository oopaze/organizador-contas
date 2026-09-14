# Cartões, fatura mensal garantida e vínculo fatura↔cartão — Design Spec

**Data:** 2026-09-14
**Status:** Aguardando revisão do usuário

## Objetivo

Organizar os cartões como entidade de primeira classe: o usuário cadastra cada cartão (nome + dia de vencimento), o sistema **garante a fatura em aberto de cada cartão todo mês** (mesmo zerada, porque a fatura é "paga" mensalmente), e o upload da fatura em PDF passa a ser **vinculado ao cartão**, estreitando a conciliação.

## Decisões de design

1. **Modelagem A**: entidade `Card` + FK opcional `Transaction.card`. Renomear cartão mantém o vínculo; a conciliação deixa de "adivinhar" pelo texto.
2. **Campos do cartão**: `name` (apelido) e `due_day` (dia de vencimento, 1–31) + `is_active`. Sem dia de fechamento/ciclo (fora de escopo).
3. **Fatura mensal garantida**: por cartão ativo/mês, uma `Transaction` "Fatura {nome} MM/AAAA" (convenção atual) com `due_date` = dia de vencimento do cartão no mês (ajustado ao fim do mês), recalculada a cada compra; zerada se não houver compras. Idempotente, mesmo espírito do `EnsureMonthlySalaryUseCase`.
4. **Upload vinculado**: o dialog de upload escolhe o cartão, com sugestão automática pelo nome do arquivo; o backend recebe `card_id` e grava na fatura importada. Sem `card_id`, mantém o comportamento atual (tolerância a clientes antigos).
5. **Conciliação por cartão**: quando a fatura importada tem cartão, as candidatas do tempo real são só as faturas em aberto **daquele cartão** (mesma janela de datas). Sem cartão, mantém a janela atual com todas.
6. **Sem tela nova de navegação**: a gestão de cartões fica em **Configurações**, seção "Cartões". O upload oferece "+ novo cartão" inline.

## Contexto verificado

- Fatura em aberto é convenção: `file=null`, `category=credit_card`, `transaction_type=outgoing`, `transaction_identifier="Fatura {rótulo} MM/AAAA"`, `due_date` = dia 1 (`quick_add.py` cria via `get_open_bill`).
- Fatura importada: `BillFactory.build_from_file` usa o identificador da IA e `BillRepository.create` grava `file` (`bill.py`, `bill_repository.py`).
- `ReconcileBillPreviewUseCase` hoje busca candidatas por janela de datas (`get_open_bills`), sem cartão.
- `EnsureMonthlySalaryUseCase` é o padrão de "garantir lançamento mensal idempotente" (`ensure_salary.py`).
- MCP `create_transaction` aceita `payment_method=credit` + `card_label` e cai no quick add.
- Convenção do cartão no quick add usa `due_date` = dia 1; passaremos a usar o `due_day` do cartão no mês da competência para não criar duas faturas do mesmo mês.

## Arquitetura

### Backend — módulo novo `modules/cards`

```
modules/cards/
├── models.py            # Card(TimedModel, UserOwnedModel, SoftDeleteModel)
├── domains/card.py
├── factories/card.py
├── repositories/card.py
├── serializers/card.py
├── use_cases/
│   ├── create.py
│   ├── list.py
│   ├── update.py
│   └── set_active.py
├── container.py
├── views.py             # CardViewSet (JWTAuthentication + IsAuthenticated)
├── urls.py              # /cards/cards/
└── migrations/0001_initial.py
```

`Card`: `name` (CharField 255), `due_day` (PositiveSmallIntegerField, default 1), `is_active` (BooleanField default True). Sem hard delete: `set_active(false)`.

Endpoints:

| Método + path | Ação |
|---|---|
| `GET /cards/cards/` | Lista cartões do usuário (todos, com flag ativo) |
| `POST /cards/cards/` | Cria cartão |
| `PATCH /cards/cards/{id}/` | Edita nome/dia |
| `POST /cards/cards/{id}/set_active/` | Ativa/desativa |

### Backend — `transactions`

- `Transaction.card` FK nullable (`related_name="transactions"`, `on_delete=SET_NULL`) + migration.
- `TransactionFactory`/`TransactionDomain`/`TransactionSerializer`/`TransactionRepository.create/update` carregam `card_id`.
- `TransactionRepository` ganha `get_open_bill_by_card(user_id, card_id, year, month)` (chave nova, usada quando há cartão) e mantém `get_open_bill(user_id, identifier, year, month)` para o fallback legado por rótulo.
- `QuickAddTransactionUseCase._execute_credit` aceita `card_id`:
  - com cartão: identifier `"Fatura {card.name} MM/AAAA"`, `due_date` = `min(card.due_day, último dia do mês)`, `card_id` no pai e nas subs? (a fatura leva o `card_id`; as subs não precisam);
  - sem cartão mas com `card_label`: comportamento legado atual (sem FK), para não quebrar MCP antigo.
- `EnsureMonthlyCardBillsUseCase` (`use_cases/transaction/ensure_card_bills.py`): para cada cartão ativo do usuário, get-or-create a fatura do mês (mesma chave do quick add), recalcula total, garante `due_date` conforme o `due_day`. Retorna as faturas. Endpoint `POST /transactions/transactions/ensure_card_bills/` com `month`.
- `ReconcileBillPreviewUseCase`: se a fatura importada tem `card_id`, candidatas = faturas em aberto com o mesmo `card_id` na janela; senão comportamento atual.

### Backend — `file_reader` (upload)

- `UploadFileUseCase`/view aceitam `card_id` opcional; `TransposeFileBillToModelsUseCase` repassa e `BillRepository.create` grava `card_id` na transação da fatura.
- Resposta do upload continua `{"message", "transaction_ids"}`.

### Migração de dados (uma só, em `transactions`)

- Faturas em aberto existentes (`file=null`, `category=credit_card`) com identificador casando `^Fatura (.+) \d{2}/\d{4}$`: cria `Card` (nome normalizado, `due_day=1`) por nome distinto e seta `card_id`.
- Faturas importadas existentes (`file≠null`, `category=credit_card`): seta `card_id` quando o identificador contém (case-insensitive) o nome de um cartão do mesmo usuário; senão fica nulo (tolerância).

### Frontend

- `services/cards/`: `getCards`, `createCard`, `updateCard`, `setCardActive`; tipos `Card` em `types.ts`.
- **Configurações**: seção "Cartões" (lista nome + "vence dia X" + ativo/inativo, modal de adicionar/editar, botão desativar/ativar).
- **Upload**: select "Cartão" no `upload-bill-dialog` com sugestão pelo nome do arquivo (case-insensitive, contém o nome do cartão) e opção "+ novo cartão" (mini-form nome + dia que cria e seleciona). Envia `card_id`.
- **Dashboard/Planejamento**: ao carregar o mês, chamam `ensureCardBills(month)` antes de buscar os dados (como o salário).
- Extrato/lista continuam mostrando "Fatura {nome} MM/AAAA".

### MCP

- `create_transaction` no cartão: aceita `card_id`; se vier `card_label`, resolve pelo nome do cartão cadastrado; sem cadastro, comportamento legado.
- Nenhuma tool nova.

## Edge cases

| Caso | Comportamento |
|---|---|
| Cartão sem compras no mês | Fatura existe zerada (garantida) e pode ser paga. |
| Renomear cartão | Faturas seguem vinculadas pela FK; novos títulos usam o novo nome. |
| Upload sem escolher cartão | Fatura importada sem FK; conciliação usa a janela de datas atual. |
| `card_label` antigo (MCP) sem cartão cadastrado | Comportamento legado (identifier com o rótulo, sem FK). |
| Fatura importada de cartão inativo | Vínculo permitido (histórico), conciliação funciona. |
| Mesmo mês, compras antes/depois | Uma única fatura por cartão/mês (chave = cartão + mês). |
| `due_day` 31 em mês curto | Ajustado para o último dia do mês. |

## Fora de escopo

- Ciclo de fechamento, limite, bandeira, Open Finance.
- Exclusão definitiva de cartão (só ativar/desativar).
- Reenvio/refazer a conciliação de faturas antigas.

## Testes

Backend (pytest, TDD nos use cases):
- `modules/cards/tests/`: create/list/update/set_active escopados por usuário.
- `transactions/tests/test_ensure_card_bills_use_case.py`: cria zerada, idempotente, usa `due_day`, só cartões ativos.
- `transactions/tests/test_quick_add_use_case.py`: cartão cadastrado não duplica fatura e grava `card_id`; fallback legado por rótulo.
- `transactions/tests/test_reconcile_bill_preview_use_case.py`: candidatas filtradas pelo cartão; fallback sem cartão.
- `file_reader/tests/test_upload_file_use_case.py`: `card_id` chega na fatura importada.
- Migração de backfill: teste de função pura de parsing do identificador.

Frontend:
- `yarn build` + `yarn test` (nav inalterado).
- Manual: criar cartão em Configurações; subir fatura com sugestão; conferir conciliação; ver a fatura do mês zerada no extrato.

## Riscos

1. **Backfill errado** cria cartões duplicados (nome com variação de caixa/espaço). Mitigação: normalizar (`strip` + casefold) antes de agrupar.
2. **Dia de vencimento x competência**: a fatura do mês é ancorada no mês da competência com o dia do vencimento; se o usuário espera "vence no mês seguinte", é só editar o dia. Documentado no hint da UI.
3. **Upload sem cartão continua possível** — comportamento tolerante, mas a conciliação fica mais larga; a UI sugere sempre.
