# 0004. Interface do MCP pode quebrar para ficar limpa

Status: Aceito
Tipo: Produto
Data: 2026-10-03

## Contexto e Problema

O MCP do Poupix está em 0.x e é consumido principalmente por agentes do próprio dono (opencode/Claude/ChatGPT). A primeira superfície espelhou o banco: `month`/`start`/`end` filtram vencimento enquanto as compras têm data própria, `category` só aceita slug mas devolve label, e há parâmetros com nomes ambíguos. As melhorias de clareza (renomear `month` → `due_month`, explicitar `purchase_*`, corrigir descrições) exigiriam manter aliases antigos ou versionar tools — o que cria duas formas de fazer a mesma coisa e confunde justamente o agente que lê as descrições.

## Motivação / Drivers

- Clareza para o agente é o principal "produto" da interface.
- Consumidores conhecidos e poucos; custo de migração baixo.
- Evitar dívida de compatibilidade prematura em uma interface 0.x.

## Opções Consideradas

- Aditivo com aliases deprecados (`month` e `due_month` convivendo).
- Versionar tools (`v2_list_transactions` etc.).
- Quebrar e limpar a interface de uma vez.

## Decisão

Escolhemos **quebrar e limpar** porque não há consumidores externos relevantes e a ambiguidade é o problema a resolver; carregar dois nomes para o mesmo conceito perpetuaria a confusão que motivou a mudança.

## Prós e Contras das Opções

### Aditivo com aliases
+ Zero quebra para clientes existentes.
- Descrições ficam ambíguas/duplicadas e a dívida nunca morre.

### Versionar tools
+ Convivência controlada entre contratos.
- Dobra a superfície e o agente não sabe qual usar.

### Quebrar e limpar
+ Interface única, descrições corretas, menos erro do agente.
- Clientes com chamadas fixas precisam se adaptar.

## Consequências

- **Positivas:** parâmetros e descrições passam a ter uma única leitura; agente erra menos.
- **Negativas:** quem fixou chamadas antigas quebra, sem janela de depreciação.
- **Riscos / Mitigações:** bump de versão no `serverInfo` (0.4.0) e atualização de `docs/MCP_SETUP.md`; o agente redescobre o contrato pelas descrições a cada sessão.
