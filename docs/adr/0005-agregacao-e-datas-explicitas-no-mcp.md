# 0005. Agregação no servidor e datas explícitas no MCP

Status: Aceito
Tipo: Produto
Data: 2026-10-03

## Contexto e Problema

Perguntas simples ("quanto gastei com X?") exigiam N+1 chamadas: listar transações do mês, buscar cada fatura com `get_transaction` e filtrar no cliente. Além do custo em tokens, o agente se confundia com `month` (vencimento da fatura) versus a data da compra (subtransação), produzindo respostas erradas para "esse mês". A regra de que a fatura de cartão é a transação canônica do mês (ADR 0003) precisa ser aplicada em um único lugar.

## Motivação / Drivers

- Menos chamadas, menos tokens e menos erro do agente.
- Semântica de datas explícita e previsível (`due_*` × `purchase_*`).
- Manter consultas read-only e escopadas, sem devolver SQL livre ao agente.

## Opções Consideradas

- Manter a agregação no agente (status quo).
- Tool de agregação no servidor (`summarize_spending`) com filtros explícitos.
- Reintroduzir SQL livre (`execute_sql`) para o agente montar as somas.

## Decisão

Escolhemos **tool de agregação no servidor** com parâmetros explícitos `due_*` (vencimento/fatura) e `purchase_*` (data da compra), porque resolve o N+1 sem devolver ao agente o poder de consulta arbitrária e mantém a regra anti-duplicação (fatura × subtransações) em um único ponto testável.

## Prós e Contras das Opções

### Agregação no agente
+ Nenhuma superfície nova.
- N+1, semântica espalhada no prompt, erro recorrente.

### Agregação no servidor
+ Uma chamada por pergunta, regra única e testável.
- Mais uma tool para manter.

### SQL livre
+ Máxima flexibilidade.
- Risco de segurança e regra de negócio duplicada/implícita no agente.

## Consequências

- **Positivas:** perguntas de gasto resolvem em uma chamada; datas ganham semântica documentada nos próprios parâmetros.
- **Negativas:** mais uma tool na superfície, com manutenção e testes próprios.
- **Riscos / Mitigações:** regra anti-duplicação coberta por testes unitários; `list_sub_transactions` cobre o nível de detalhe quando a agregação não bastar.
