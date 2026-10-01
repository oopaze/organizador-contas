# 0002. Offline somente leitura no app Android

Status: Aceito
Tipo: Produto
Data: 2026-10-01

## Contexto e Problema

O app nasce com motivação de funcionar sem internet. Dado financeiro desatualizado ou duplicado tem risco real: lançar offline exige idempotência no backend, fila de envio, resolução de conflito e UI de pendências. Qual profundidade de offline o app deve ter nesta fase?

## Motivação / Drivers

- Usabilidade sem rede sem comprometer a confiança nos dados
- Backend não deve mudar nesta fase
- Menor superfície de erro em lógica de sincronização

## Opções Consideradas

- Sem cache de dados (só a casca, como o PWA hoje)
- Cache de leitura (dados persistidos no aparelho, escrita exige rede)
- Leitura e escrita offline (fila idempotente)

## Decisão

Escolhemos **cache de leitura**: toda leitura responde do último sync persistido (react-query + AsyncStorage) com aviso do horário dos dados; qualquer escrita exige conexão e falha com erro honesto. Porque entrega o valor principal (consultar sem rede) sem introduzir o problema de consistência de escrita offline.

## Prós e Contras das Opções

### Sem cache

+ Nenhuma complexidade nova; comportamento idêntico ao PWA atual
- Sem rede o app não mostra nada; não atende à motivação original

### Cache de leitura

+ Consulta offline com aviso claro do horário dos dados; sem fila, sem conflito; backend intacto
- Lançamentos offline não existem; escrever exige conexão

### Leitura e escrita offline

+ App usável por completo sem rede, incluindo lançamentos
- Exige idempotência no backend, fila, conflitos e UI de pendências; risco de duplicar dinheiro

## Consequências

- **Positivas:** confiança nos dados (nunca mostra dado novo sem fonte); escopo enxuto e sem mudança de backend.
- **Negativas:** não dá para lançar sem rede — o caso "lançar no metrô" fica para uma fase futura.
- **Riscos / Mitigações:** cache velho enganar o usuário — banner com timestamp do último sync em todas as telas com dados; evolução para escrita offline exigirá novo ADR com idempotência no backend.
