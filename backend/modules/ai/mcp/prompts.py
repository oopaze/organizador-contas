PROMPTS = [
    {
        "name": "resumo_mensal",
        "description": "Resumo dos gastos de um mês por categoria, com comparativo do mês anterior.",
        "arguments": [
            {
                "name": "mes",
                "description": "Mês no formato YYYY-MM (padrão: mês corrente)",
                "required": False,
            },
        ],
    },
    {
        "name": "onde_cortar_gastos",
        "description": "Analisa os últimos 3 meses por categoria e sugere cortes em gastos discricionários.",
        "arguments": [],
    },
]


from django.utils import timezone


def _previous_month(mes: str) -> str | None:
    try:
        year, month = int(mes[:4]), int(mes[5:7])
    except ValueError:
        return None
    if month == 1:
        return f"{year - 1}-12"
    return f"{year}-{month - 1:02d}"


def list_prompts() -> list[dict]:
    return PROMPTS


def get_prompt(name: str, arguments: dict | None = None) -> dict | None:
    arguments = arguments or {}
    if name == "resumo_mensal":
        mes = (arguments.get("mes") or "").strip() or timezone.localdate().strftime("%Y-%m")
        anterior = _previous_month(mes)
        comparacao = (
            f"e due_month={anterior} para o mês anterior, e compare"
            if anterior
            else "e compare com o mês anterior"
        )
        texto = (
            f"Faça um resumo dos meus gastos de {mes}. "
            f"Use summarize_spending com due_month={mes} e group_by=category para {mes} "
            f"{comparacao}. Apresente o total do mês, as categorias que mais pesaram "
            "e a variação em relação ao mês anterior."
        )
        return {
            "description": PROMPTS[0]["description"],
            "messages": [{"role": "user", "content": {"type": "text", "text": texto}}],
        }
    if name == "onde_cortar_gastos":
        texto = (
            "Analise meus gastos dos últimos 3 meses com summarize_spending "
            "(group_by=category, purchase_month quando útil). Aponte as categorias "
            "discricionárias (lazer, delivery, assinaturas, lifestyle) que mais pesam "
            "e sugira cortes concretos com valores."
        )
        return {
            "description": PROMPTS[1]["description"],
            "messages": [{"role": "user", "content": {"type": "text", "text": texto}}],
        }
    return None
