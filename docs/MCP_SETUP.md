# MCP Poupix — Setup local

Este guia configura o servidor MCP do Poupix (v0.4.0) para uso com Claude Desktop,
Claude Code ou opencode.

## Pré-requisitos

- Banco e Redis rodando (`docker compose -f docker-compose.api.yml up -d db redis`).
- Backend Python instalado (`pip install -r backend/requirements.txt`).
- Migrations aplicadas (`make migrate`).

## 1. Descobrir seu user_id

```bash
cd backend
python manage.py mcp_whoami seu-email@exemplo.com
```

Saída: `user_id = 7  (use this as POUPIX_MCP_USER_ID)`. Anote esse número — o
transporte stdio usa esse id para escopar todas as tools ao seu usuário.

## 2. Configurar o cliente MCP

### Claude Desktop

Abra `%APPDATA%\Claude\claude_desktop_config.json` (Windows) ou `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) e adicione:

```json
{
  "mcpServers": {
    "poupix": {
      "command": "python",
      "args": ["manage.py", "run_mcp"],
      "cwd": "C:/Users/Pedro/Documents/projtos/organizador-contas-main/backend",
      "env": {
        "POUPIX_MCP_USER_ID": "7"
      }
    }
  }
}
```

Substitua `cwd` pelo caminho absoluto do seu repositório, e `POUPIX_MCP_USER_ID` pelo seu user_id.

### Claude Code / opencode

Use o mesmo bloco acima no seu cliente (`~/.claude/mcp.json`, `opencode.json` etc.).
No opencode, os prompts do servidor aparecem como `/poupix:resumo_mensal` e
`/poupix:onde_cortar_gastos`.

## 3. Reiniciar o cliente MCP e testar

Reinicie Claude Desktop / Claude Code / opencode. Em uma conversa nova, peça:

> "Quais foram minhas 5 maiores despesas dos últimos 30 dias?"

O agente deve usar `list_enums` para resolver a categoria, `summarize_spending`
para totais e/ou `list_sub_transactions` para listar as compras.

## Ferramentas expostas

| Tool | Parâmetros | O que faz |
|---|---|---|
| `list_transactions` | `due_month`, `due_start`, `due_end`, `transaction_type`, `category`, `paid`, `search`, `include_subtransactions`, `limit` | Lista transações (faturas/documentos). `search` casa o identificador ou a descrição das compras. |
| `get_transaction` | `transaction_id`* | Retorna a transação e suas subtransações. |
| `create_transaction` | `transaction_identifier`*, `total_amount`*, `due_date`*, `transaction_type`, `payment_method`, `card_label`, `card_id`, `installments`, `category`, `is_salary`, `is_recurrent`, `recurrence_count`, `is_paid`, `paid_at`, `actor_id` | Cria um lançamento. Com `payment_method` (`cash`/`credit`) usa o lançamento rápido — cartão entra na fatura em aberto e aceita parcelas; sem `payment_method` cria direto. |
| `update_transaction` | `transaction_id`*, `transaction_identifier`, `total_amount`, `due_date`, `transaction_type`, `category`, `is_salary` | Atualiza campos da transação. |
| `create_sub_transaction` | `transaction_id`*, `description`*, `amount`*, `date`, `category`, `installment_info`, `paid_at`, `actor_id` | Adiciona uma compra (subtransação) a uma fatura. |
| `update_sub_transaction` | `sub_transaction_id`*, `description`, `amount`, `date`, `category`, `installment_info`, `user_provided_description`, `actor` | Atualiza uma compra. |
| `list_sub_transactions` | `purchase_month`, `purchase_start`, `purchase_end`, `due_month`, `due_start`, `due_end`, `category`, `search`, `transaction_id`, `actor_id`, `limit` | Lista compras de forma plana e filtrável. |
| `summarize_spending` | `due_month`, `due_start`, `due_end`, `purchase_month`, `purchase_start`, `purchase_end`, `category`, `search`, `transaction_type`, `group_by` | Soma gastos/entradas com agrupamento no servidor (`none`, `category`, `card`, `month`). Use para "quanto gastei com X". |
| `get_projection` | `start`, `end`, `months` | Projeção mensal (padrão 12): renda garantida menos as parcelas planejadas, com a sobra de cada mês. |
| `set_goals` | `spending_goal_percent`, `savings_goal_percent`, `essentials_goal_percent` | Atualiza metas financeiras em % da renda (0–100). |
| `list_enums` | — | Slugs/labels válidos para `category` e `transaction_type`. |
| `list_cards` | — | Cartões do usuário (id, nome, dia de vencimento, ativo). |
| `list_actors` | — | Atores/pessoas do usuário (id, nome). |

\* parâmetro obrigatório. Valores monetários em BRL.

### Semântica de datas: `due_*` vs `purchase_*`

- `due_month` / `due_start` / `due_end` (YYYY-MM / YYYY-MM-DD) filtram o **vencimento** da fatura/documento. "Esse mês" normalmente significa a fatura do mês.
- `purchase_month` / `purchase_start` / `purchase_end` filtram a **data da compra** (subtransações; em transação sem subtransações vale o vencimento).
- Modelo canônico: cada cartão tem uma transação por mês ("Fatura {cartão} MM/AAAA") cujo `due_date` é o vencimento; as compras são subtransações com `date` próprio.
- Em `summarize_spending`, fatura de cartão conta pelas subtransações (nunca pelo total); transação sem subtransações conta o total. IOF de compras internacionais aparece como item próprio quando existir.

## Instructions

No handshake (`initialize`), o servidor devolve `instructions` ao agente com o
contexto essencial: dados já escopados ao usuário do token (nunca pedir
`user_id`), valores em BRL, somente leitura, o modelo canônico da fatura, a
diferença entre `due_*` e `purchase_*`, uso de `list_enums`/`summarize_spending`
e a regra do IOF.

## Prompts

| Prompt | Argumentos | O que faz |
|---|---|---|
| `resumo_mensal` | `mes` (YYYY-MM, opcional; padrão mês corrente) | Resumo dos gastos do mês por categoria, comparando com o mês anterior. |
| `onde_cortar_gastos` | — | Analisa os últimos 3 meses e sugere cortes em gastos discricionários. |

No opencode aparecem como `/poupix:resumo_mensal` e `/poupix:onde_cortar_gastos`.

## Breaking changes da 0.4.0

- Filtros renomeados para explicitar a data filtrada: `month` → `due_month`,
  `start` → `due_start`, `end` → `due_end`.
- As tools `execute_sql` e `describe_schema` foram removidas; a superfície
  passou a ser tipada (as 13 tools acima).

## Segurança

O servidor é seguro em duas camadas:

1. **Escopo automático ao usuário** — no transporte HTTP o usuário vem do token
   OAuth (`Bearer`); no stdio, de `POUPIX_MCP_USER_ID`. As tools nunca aceitam
   `user_id` como parâmetro.
2. **Somente leitura e superfície tipada** — não há SQL livre: cada tool executa
   um caso de uso com filtros validados (datas, `category` resolve slug/label,
   `group_by` restrito) e consultas já filtradas por usuário e soft-deleted.

## Troubleshooting

- **`POUPIX_MCP_USER_ID is required`** — o cliente MCP não exportou a variável; verifique o `env` no bloco do `mcp.json`.
- **`user_id = ...` não encontrado no `mcp_whoami`** — confira o e-mail; o comando falha se o usuário não existir.
- **HTTP 401 `invalid_token`** — token OAuth ausente, inválido ou expirado; refaça o fluxo de autorização do cliente.
