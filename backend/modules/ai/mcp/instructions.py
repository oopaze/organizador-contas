SERVER_VERSION = "0.4.0"

SERVER_INSTRUCTIONS = """Servidor MCP do Poupix: finanças pessoais do usuário autenticado, em BRL, somente leitura.
- Todos os dados já são escopados ao usuário do token; nunca peça user_id.
- Modelo: cada cartão tem uma transação canônica por mês ("Fatura {cartão} MM/AAAA") cujo due_date é o vencimento; as compras são subtransações com date próprio (data da compra).
- Datas: parâmetros due_* filtram o vencimento (fatura); purchase_* filtram a data da compra. "Esse mês" normalmente significa a fatura do mês.
- Categorias: consulte list_enums; a entrada aceita slug ou label; as respostas trazem category (label) e category_slug.
- Para "quanto gastei com X", use summarize_spending. Para listar compras, use list_sub_transactions. Para faturas/documentos, use list_transactions.
- IOF de compras internacionais entra como item próprio quando existir.
"""
