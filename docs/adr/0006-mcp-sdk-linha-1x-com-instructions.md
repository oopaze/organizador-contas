# 0006. MCP SDK na linha 1.x com instructions first-class

Status: Aceito
Tipo: Técnica
Data: 2026-10-03

## Contexto e Problema

O projeto fixa `mcp==1.2.0`, que não suporta `instructions` no handshake — o agente não recebe contexto de domínio (fatura canônica, BRL, escopo por usuário). A linha 2.x do SDK reescreveu a API do servidor (handlers no construtor, sem decorators), o que exigiria reescrever o transporte stdio. A última 1.x (1.30.0) mantém a API de decorators usada hoje e adiciona `instructions` first-class, além de suportar prompts.

## Motivação / Drivers

- Contexto para o agente é uma melhoria central desta entrega.
- Minimizar custo de migração e risco de regressão.
- Manter os dois transportes (stdio e HTTP) com o mesmo contrato.

## Opções Consideradas

- Ficar no 1.2 e enviar `instructions` apenas no HTTP (stdio fica sem).
- Subir para a última 1.x (`mcp==1.30.0`).
- Migrar para o 2.x.

## Decisão

Escolhemos **subir para 1.30.0** porque entrega `instructions` e prompts sem reescrever o servidor, preservando a superfície de API já usada; a migração para 2.x fica para quando o custo se justificar.

## Prós e Contras das Opções

### Ficar no 1.2 (instructions só no HTTP)
+ Zero risco de upgrade.
- A melhoria principal não chega ao stdio e os transportes divergem.

### 1.30.0
+ `instructions` e prompts nos dois transportes, API estável.
- Atualização de dependência a validar com a suíte.

### 2.x
+ Linha atual do SDK.
- Reescrita do transporte stdio e risco alto neste momento.

## Consequências

- **Positivas:** mesmo contrato nos dois transportes; prompts disponíveis para clientes que os suportam.
- **Negativas:** dívida de upgrade para 2.x acumula.
- **Riscos / Mitigações:** pin exato `mcp==1.30.0` e suíte como gate; contingência registrada no spec (instructions apenas no HTTP se houver incompatibilidade).
