# 0003. Fatura mensal do cartão é a transação canônica do mês

Status: Aceito
Tipo: Produto
Data: 2026-10-03

## Contexto e Problema

Com o Modo On, compras de cartão lançadas em tempo real vivem na "fatura em aberto" (nome
`Fatura {cartão} MM/AAAA`, sem arquivo) e o upload do PDF criava uma transação importada
paralela. A conciliação casava as compras em tempo real com as linhas do PDF e só encerrava a
fatura em aberto quando ela ficava sem lançamentos.

Com a fatura mensal garantida por cartão, isso passou a duplicar o mês: quando a fatura em
aberto estava zerada não havia par para conciliar, então ela nunca era encerrada. O extrato
mostrava, ao mesmo tempo, `Fatura C&A Pay 10/2026` (zerada) e `C&A Pay` (importada), além de o
próximo lançamento no cartão criar uma terceira fatura em aberto do mesmo mês.

## Motivação / Drivers

- Uma única transação por cartão/mês, com o título mensal previsível (`Fatura {cartão} MM/AAAA`).
- O upload deve alimentar a fatura do mês, não criar uma entidade paralela.
- Preservar a conciliação (pares tempo real × PDF) quando o usuário já lançou compras antes.

## Opções Consideradas

- Manter a transação importada como canônica e encerrar a fatura em aberto quando ela estivesse vazia.
- Tornar a fatura mensal do cartão canônica: o upload escreve nela e a importada é absorvida.
- Não mudar nada; o usuário apaga a duplicada manualmente.

## Decisão

Escolhemos **tornar a fatura mensal do cartão a transação canônica** porque é ela que o usuário
acompanha e paga todo mês. A transação importada passa a ser transitória: quando a fatura do mês
está sem lançamentos, o PDF escreve direto nela; quando já há lançamentos em tempo real, a
conciliação continua abrindo, e ao aplicar a fatura mensal absorve os lançamentos e a importada
é encerrada.

## Prós e Contras das Opções

### Importada canônica (com encerramento da fatura vazia)
+ Correção menor, restrita ao encerramento da fatura sem lançamentos.
- O título do mês vira o nome do PDF (`C&A Pay`) e a fatura mensal desaparece, contrariando a
  expectativa de continuidade do cartão.

### Fatura mensal canônica
+ Mantém um único título por mês e a fatura acumula os lançamentos do PDF.
+ Preserva a conciliação quando há lançamentos em tempo real.
- Exige absorver a importada na conciliação e fazer o lookups por cartão/mês enxergar a fatura
  já importada.

## Consequências

- **Positivas:** uma transação por cartão/mês; upload alimenta a fatura do mês; lançamento rápido
  e garantia mensal encontram a fatura mesmo depois de importada.
- **Negativas:** a conciliação aplicada deixa de ter a importada como registro canônico; clientes
  antigos que não informam a fatura mensal ao conciliar mantêm o comportamento anterior.
- **Riscos / Mitigações:** os duplicados já existentes precisam de correção pontual; a absorção
  preserva as anotações do usuário e só encerra a importada depois de mover os lançamentos.
