# MCP do Poupix 0.4 — superfície orientada ao agente (Design Spec)

**Data:** 2026-10-03
**Status:** Proposto — aguardando revisão
**Branch:** `feat/mcp-superficie-agente`
**ADRs:** 0004 (breaking permitido), 0005 (agregação + datas explícitas), 0006 (SDK 1.x com instructions)

## Objetivo

Deixar a superfície do MCP do Poupix **orientada às perguntas reais do agente** ("quanto gastei com X?", "quais compras do mês passado?"), eliminando chamadas N+1, ambiguidade de datas, categorias opacas e falta de contexto. A interface atual (0.3) foi desenhada para espelhar o banco; a 0.4 é desenhada para o agente responder em **uma ou duas chamadas**.

## Contexto verificado (2026-10-03)

Uso real do MCP em sessão de agente expôs:

1. **`list_transactions` mente na descrição**: promete "com as subtransações", mas retorna `sub_transactions: []`. Causa: `TransactionFactory.build_from_model` não hidrata subs; só `GetTransactionUseCase` chama `set_sub_transactions`. Resultado prático: 1 `list` + N `get_transaction` para qualquer pergunta de gasto.
2. **`month`/`start`/`end` ambíguos**: filtram `due_date` (vencimento da fatura), enquanto as compras têm `date` próprio (subtransação). "Gastei esse mês" tem duas leituras e o agente escolhe errado.
3. **Categorias só como label na saída** ("Transporte - Combustível"): o agente precisa garimpar por regex; o input exige slug, a saída devolve label — assimetria que induz erro.
4. **`search` só cobre `transaction_identifier`**: procurar "posto" ou "anthropic" não acha nada, porque as compras são subtransações.
5. **Ids opacos**: `card_id`/`actor_id` não têm tool para resolver (`list_cards`/`list_actors` não existem).
6. **Sem `instructions` nem prompts**: nenhum contexto de domínio (fatura canônica, BRL, escopo por usuário) e nenhum workflow pronto.
7. **SDK `mcp==1.2.0`**: não suporta `instructions` no `initialize` (nem stdio nem tipos); `prompts` existe mas não é registrado.

Restrições do código (mapeadas):

- `TransactionRepository.filter(filters)` usa `queryset.filter(**filters)` — não expressa OR (necessário para search em subs).
- `SubTransactionRepository` tem `get_by_date_range`, `get_all_by_transaction_ids`, `filter_by_actor_id(s)` — falta um `filter(user_id, filters)` genérico.
- `CardsContainer` é standalone (`list_cards_use_case` pronto); actors já estão em `TransactionsContainer.list_actors_use_case`.
- `TransactionSerializer` devolve label em `category`; `SubTransactionSerializer` idem com fallback "Outros".
- Transportes compartilham `TOOLS` + `dispatch_tool` (`tools/__init__.py`); HTTP é JSON-RPC manual (`http/views.py`), stdio usa o SDK (`server.py`).

## Decisões

- **0004** — A interface pode quebrar para ficar limpa (sem aliases/versão de tools).
- **0005** — Agregação no servidor + parâmetros explícitos `due_*` vs `purchase_*`.
- **0006** — SDK `mcp==1.30.0` (mantém decorators e ganha `instructions`); 2.x fora de escopo.

## Contrato das tools (0.4)

### Mudanças nas existentes

| Tool | Mudança |
|---|---|
| `list_transactions` | **Breaking:** `month` → `due_month`; `start`/`end` → `due_start`/`due_end`. Novo `include_subtransactions` (default `false`). `search` passa a casar `transaction_identifier` **ou** descrição de subtransação. `category` aceita slug **ou** label. Saída ganha `category_slug`. |
| `get_transaction` | Compatível; saída ganha `category_slug` (transação e subs). |
| `list_enums` | Sem mudança (já devolve slug + label). |
| `create_transaction`, `update_transaction`, `create_sub_transaction`, `update_sub_transaction` | Compatíveis; `category` aceita slug ou label; descrições ganham exemplos e "valores em BRL". |
| `get_projection`, `set_goals` | Compatíveis; descrições revisadas. |

`list_transactions` (args): `due_month` (YYYY-MM), `due_start`/`due_end` (YYYY-MM-DD), `transaction_type` (`incoming|outgoing`), `category`, `paid` (bool), `search`, `include_subtransactions` (bool, default `false`), `limit` (default 50, máx 200).
Resposta: `{ "transactions": [...], "count": N }`; com `include_subtransactions=true`, cada transação traz suas subs hidratadas em lote.

### Novas tools

**`list_sub_transactions`** — lista compras (linhas de fatura) de forma plana e filtrável.

Args: `purchase_month` (YYYY-MM), `purchase_start`/`purchase_end` (YYYY-MM-DD), `due_month`, `due_start`/`due_end` (filtram o vencimento da fatura pai), `category`, `search` (descrição), `transaction_id`, `actor_id`, `limit` (default 100, máx 200).
Resposta: `{ "sub_transactions": [...], "count": N }`. Item: `id`, `date`, `description`, `amount`, `category` (label), `category_slug`, `actor` (ou null), `transaction_id`, `transaction_identifier`, `card_id`, `installment_info`, `paid_at`.

**`summarize_spending`** — soma gastos/ganhos com filtros e agrupamento no servidor.

Args: `due_month`/`due_start`/`due_end`, `purchase_month`/`purchase_start`/`purchase_end`, `category`, `search`, `transaction_type` (`incoming|outgoing`, default `outgoing`), `group_by` (`none|category|card|month`, default `none`).
Resposta: `{ "total": "321.46", "count": N, "currency": "BRL", "groups": [{ "key": "...", "label": "...", "total": "...", "count": N }] }`.

**Regra anti-duplicação (obrigatória):** para transações **com** subtransações, conta-se apenas as subs (nunca o `total_amount` da fatura); para transações **sem** subs, conta-se o `total_amount`. Os filtros `purchase_*`, `category` e `search` são aplicados **por item** (sub ou transação sem subs); `due_*` e `transaction_type` filtram a transação pai. No `group_by=month`, a data usada segue a base do filtro: com `purchase_*`, é a `date` do item; com `due_*` ou sem filtro, é o `due_date` da transação pai (na transação sem subs, o próprio item já usa o `due_date`).

**`list_cards`** — `{ "cards": [{ "id", "name", "due_day", "is_active" }] }` (via `CardsContainer.list_cards_use_case`).

**`list_actors`** — `{ "actors": [{ "id", "name" }] }` (via `ListActorsUseCase` com `without_sub_transactions=True`, reduzido a id/nome).

Total: **9 → 13 tools**.

## Semântica de datas

- `due_*` = vencimento da fatura/documento (transação pai). É o "mês" que o app mostra por padrão.
- `purchase_*` = data da compra (subtransação).
- Formatos: `YYYY-MM` para `*_month`, `YYYY-MM-DD` para `*_start`/`*_end`; entradas inválidas → erro `INVALID_DATE` com o formato esperado.
- `*_month` e `*_start`/`*_end` são combináveis (AND); recomenda-se usar um ou outro.

## Arquitetura

**Domínio (`modules/transactions`):**

- `SummarizeSpendingUseCase` (novo, `use_cases/transaction/summarize_spending.py`): recebe filtros normalizados, usa `TransactionRepository.filter` + `SubTransactionRepository.get_all_by_transaction_ids`, aplica a regra anti-duplicação e agrupa. Depende também de `card_repository` para o label de `group_by=card`. Provider `summarize_spending_use_case` no `TransactionsContainer`.
- `ListSubTransactionsUseCase.execute(user_id, filters: dict | None = None)`: extensão retrocompatível (a assinatura atual `due_date`/`actor_id` continua funcionando) mapeando para `SubTransactionRepository.filter(user_id, filters)` (novo método com `transaction__due_date__*`, `date__*`, `category`, `description__icontains`, `transaction_id`, `actor_id`).
- `ListTransactionsUseCase.execute(filters, include_subtransactions=False)`: com a flag, hidrata em lote via `SubTransactionRepository.get_all_by_transaction_ids` + `set_sub_transactions` antes de serializar. Injeta `sub_transaction_repository` no provider.
- `TransactionRepository.filter`: tratar `search` com OR (`transaction_identifier__icontains` OU `sub_transactions__description__icontains`) e `distinct()`; demais chaves seguem `filter(**filters)`.

**Adapter MCP (`modules/ai/mcp`):**

- `tools/__init__.py`: `TOOLS` continua sendo o registry declarativo; `dispatch_tool` vira **registry dict** `{nome: handler}`; teste de contrato garante que todo `TOOLS` tem handler.
- Novos módulos de handler: `tools/sub_transactions.py`, `tools/spending.py`, `tools/directory.py` (cards + actors). `tools/transactions.py` ganha os helpers de categoria.
- Helpers compartilhados: `resolve_category(value) -> slug` (aceita slug ou label; erro `INVALID_CATEGORY` com dica do `list_enums`), `enrich_category_slug(dict) -> dict`.
- `MCPContainer` ganha `cards_container` (`CardsContainer`).
- `instructions` em módulo próprio (`mcp/instructions.py`) e prompts em `mcp/prompts.py` (registry `PROMPTS` + `get_prompt(name, arguments)`), compartilhados pelos dois transportes.

**Transportes:**

- HTTP (`http/views.py`): `initialize` devolve `instructions` e capability `prompts`; novos branches `prompts/list` e `prompts/get`.
- stdio (`server.py`): `Server("poupix-mcp", version="0.4.0", instructions=SERVER_INSTRUCTIONS)`; `register_tools` registra `list_prompts`/`get_prompt` via decorators.
- `SERVER_INFO` → `0.4.0`.

## Instructions (conteúdo)

Texto único enviado no `initialize`, cobrindo: dados do usuário autenticado (BRL, read-only, nunca pedir `user_id`); modelo de fatura mensal canônica (uma transação por cartão/mês, compras = subtransações); semântica `due_*` vs `purchase_*`; uso de `list_enums` para categorias; guia de escolha ("quanto gastei" → `summarize_spending`; compras → `list_sub_transactions`; faturas → `list_transactions`); IOF entra como item quando existir.

## Prompts (conteúdo)

- `resumo_mensal` (arg opcional `mes` YYYY-MM, default mês corrente): orienta `summarize_spending` do mês com `group_by=category` + comparativo com o mês anterior, apresentando top categorias e total.
- `onde_cortar_gastos` (sem args): orienta resumo dos últimos 3 meses por categoria, destacando gastos discricionários (lazer, delivery, assinaturas, lifestyle) e sugerindo cortes.

## Erros acionáveis

Formato atual mantido (`{"error": {"code", "message"}}` + `isError`). Códigos: `INVALID_CATEGORY` (com dica e exemplo do `list_enums`), `INVALID_DATE` (formato esperado), `UNKNOWN_TOOL` (lista as tools válidas), `TOOL_ERROR` (fallback atual).

## Compatibilidade e migração

- Breaking apenas em `list_transactions` (`month`/`start`/`end` → `due_*`); as demais mudanças são aditivas.
- `docs/MCP_SETUP.md` está desatualizado (ainda descreve `execute_sql`) e será reescrito com a tabela das 13 tools, instructions e prompts.
- Teste HTTP existente espera 8 tools (stale) e será atualizado para o contrato novo.
- Nenhuma migração de banco.

## Testes

- **Unit (SimpleTestCase + Mock):** builders de filtros das novas tools; `resolve_category`; `enrich_category_slug`; registry de dispatch (contrato TOOLS→handler); `get_prompt`; códigos de erro.
- **Unit do domínio (Mock):** `SummarizeSpendingUseCase` — regra anti-duplicação (fatura com subs não soma total; transação sem subs soma total), filtros por item, `group_by` (category/card/month/none).
- **Integração (Django TestCase, `MCP_PG_INTEGRATION=1`):** `list_transactions` com `include_subtransactions`; `list_sub_transactions` filtros; `summarize_spending` ponta a ponta; `initialize` (instructions + capability prompts); `prompts/list` e `prompts/get`; `tools/list` com 13.
- **Regressão:** suíte existente do MCP e de transactions verde após os renames.

## Configuração

Nada configurável por ambiente: instructions, prompts, versão e limites são **constantes de código** (sem `.env`, sem feature flag). O único valor de dependência é o pin `mcp==1.30.0` no `requirements.txt`.

## Riscos e mitigações

- **Upgrade 1.2 → 1.30:** validado em probe (decorators mantidos, `instructions` first-class). Mitigação: primeira task do plano sobe o pin e roda a suíte; se houver incompatibilidade, o contingente é manter 1.2 e enviar `instructions` só no HTTP (registrado, não silencioso).
- **Payload de `include_subtransactions`:** `limit` limita transações, não subs. Mitigação: documentar na descrição e manter default `false`.
- **Quebra de clientes:** descrições novas guiam o agente; docs atualizados. Mitigação: bump 0.4.0 no `serverInfo`.

## Entregas de alto nível

1. SDK 1.30 + `instructions` + prompts (plumbing nos dois transportes).
2. Recontrato: renames `due_*`, categoria slug|label + `category_slug`, search em subs, `include_subtransactions`.
3. `list_sub_transactions` (repo filter + use case + tool).
4. `summarize_spending` (use case + tool).
5. `list_cards` + `list_actors`.
6. Erros acionáveis, docs (`MCP_SETUP.md`), testes stale, bump 0.4.0.

## Fora de escopo

- Deploy em produção (combinado à parte).
- Mudanças na UI e no chat IA do app.
- Migração para o SDK MCP 2.x.
