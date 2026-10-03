# MCP Poupix 0.4 — superfície orientada ao agente (Implementation Plan)

> **For agentic workers:** Use the `dev-executar-plano` skill to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar a superfície 0.4 do MCP do Poupix: datas explícitas (`due_*`/`purchase_*`), agregação no servidor, 4 tools novas, categorias slug+label, instructions e prompts — respondendo "quanto gastei com X" em uma chamada.

**Architecture:** O contrato vive em `backend/modules/ai/mcp/tools/` (registry declarativo `TOOLS` + registry de handlers), com regra de negócio nos use cases de `modules/transactions` (agregação e filtros). Os dois transportes (HTTP JSON-RPC manual e stdio via SDK) compartilham `TOOLS`, `PROMPTS` e `instructions`.

**Tech Stack:** Python 3.12, Django 6, dependency-injector, `mcp==1.30.0`, pytest.

**Spec:** `docs/specs/2026-10-03-mcp-superficie-agente-design.md`

## Global Constraints

- Pin exato `mcp==1.30.0` no `backend/requirements.txt` (spec/ADR 0006).
- Nada configurável por ambiente: instructions, prompts, versão e limites são **constantes de código** (sem `.env`, sem feature flag).
- Breaking é permitido e esperado: `month`/`start`/`end` de `list_transactions` viram `due_month`/`due_start`/`due_end` (ADR 0004).
- Categoria: slug é a chave interna; a resposta traz `category` (label) **e** `category_slug`; a entrada aceita slug **ou** label.
- Valores monetários em BRL, string decimal com 2 casas (ex.: `"100.00"`).
- Sem migrações de banco. Única mudança em serializer de app: campo aditivo `card_id` em `SubTransactionSerializer`.
- Textos, docs e commits em pt-BR; commits no formato `{verbo}: {descrição}`.
- Suíte unit: `cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/ modules/transactions/tests/ -q`
- Suíte de integração HTTP: `cd backend && MCP_PG_INTEGRATION=1 /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/http/tests/test_mcp_view.py -q`

## Review Focus

1. `summarize_spending` com filtro `category` numa fatura com subs variadas: só as subs da categoria contam — o `total_amount` da fatura não pode vazar (anti-duplicação sob filtro).
2. `list_transactions` com `search` que casa **só** a descrição de uma sub: a transação pai aparece uma única vez (`distinct`), e `count` respeita o `limit`.
3. `purchase_month`/`purchase_start`/`purchase_end` em transação **sem** subs (pix/dinheiro): a data do item é o `due_date`, não pode ser excluída.
4. Categoria inválida na entrada → `INVALID_CATEGORY` acionável; label acentuada (`"Transporte - Combustível"`) resolve para `transport_fuel`.
5. `include_subtransactions=true` em transação sem subs → `sub_transactions: []` (nunca `null`), e fatura com subs não tem o total somado junto das subs.

---

### Task 1: SDK 1.30 + instructions nos dois transportes

**Files:**
- Modify: `backend/requirements.txt:23`
- Create: `backend/modules/ai/mcp/instructions.py`
- Modify: `backend/modules/ai/mcp/http/views.py:23-24,30-38`
- Modify: `backend/modules/ai/mcp/server.py:28-36`
- Test: `backend/modules/ai/mcp/tests/test_instructions.py`

**Interfaces:**
- Produces: `SERVER_VERSION: str` (`"0.4.0"`) e `SERVER_INSTRUCTIONS: str` em `modules.ai.mcp.instructions`, usados por `http/views.py` e `server.py`.

- [ ] **Step 1: Subir o pin e instalar**

Edite `backend/requirements.txt` linha 23 para `mcp==1.30.0` e rode:

```bash
cd backend && /tmp/opencode/venv/bin/pip install -q "mcp==1.30.0" && /tmp/opencode/venv/bin/pip show mcp | grep Version
```

Esperado: `Version: 1.30.0`. Rode a suíte unit para garantir que o upgrade não quebrou nada:

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/ -q
```

Esperado: `25 passed`.

- [ ] **Step 2: Escrever o teste que falha**

Crie `backend/modules/ai/mcp/tests/test_instructions.py`:

```python
from django.test import SimpleTestCase

from modules.ai.mcp import instructions
from modules.ai.mcp.http import views


class TestServerInstructions(SimpleTestCase):
    def test_initialize_includes_instructions_and_version(self):
        response = views._dispatch(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize"}, user_id=1
        )

        result = response["result"]
        self.assertEqual(result["serverInfo"]["version"], "0.4.0")
        self.assertEqual(result["instructions"], instructions.SERVER_INSTRUCTIONS)
        self.assertIn("fatura", instructions.SERVER_INSTRUCTIONS.lower())
```

- [ ] **Step 3: Rodar e ver falhar**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/test_instructions.py -q
```

Esperado: FAIL com `KeyError: 'instructions'`.

- [ ] **Step 4: Implementar `instructions.py`**

Crie `backend/modules/ai/mcp/instructions.py`:

```python
SERVER_VERSION = "0.4.0"

SERVER_INSTRUCTIONS = """Servidor MCP do Poupix: finanças pessoais do usuário autenticado, em BRL, somente leitura.
- Todos os dados já são escopados ao usuário do token; nunca peça user_id.
- Modelo: cada cartão tem uma transação canônica por mês ("Fatura {cartão} MM/AAAA") cujo due_date é o vencimento; as compras são subtransações com date próprio (data da compra).
- Datas: parâmetros due_* filtram o vencimento (fatura); purchase_* filtram a data da compra. "Esse mês" normalmente significa a fatura do mês.
- Categorias: consulte list_enums; a entrada aceita slug ou label; as respostas trazem category (label) e category_slug.
- Para "quanto gastei com X", use summarize_spending. Para listar compras, use list_sub_transactions. Para faturas/documentos, use list_transactions.
- IOF de compras internacionais entra como item próprio quando existir.
"""
```

- [ ] **Step 5: Usar as constantes no HTTP e no stdio**

Em `backend/modules/ai/mcp/http/views.py`, importe e ajuste:

```python
from modules.ai.mcp.instructions import SERVER_INSTRUCTIONS, SERVER_VERSION

SERVER_INFO = {"name": "poupix-mcp", "version": SERVER_VERSION}
```

e no branch `initialize` do `_dispatch`, inclua `instructions`:

```python
    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": rid,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
                "instructions": SERVER_INSTRUCTIONS,
            },
        }
```

Em `backend/modules/ai/mcp/server.py`, importe `SERVER_INSTRUCTIONS, SERVER_VERSION` e troque a criação do server:

```python
    server = Server("poupix-mcp", version=SERVER_VERSION, instructions=SERVER_INSTRUCTIONS)
```

- [ ] **Step 6: Rodar os testes**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/ -q
```

Esperado: `26 passed` (25 + o novo).

- [ ] **Step 7: Commit**

```bash
git add backend/requirements.txt backend/modules/ai/mcp/instructions.py backend/modules/ai/mcp/http/views.py backend/modules/ai/mcp/server.py backend/modules/ai/mcp/tests/test_instructions.py
git commit -m "feat: adiciona instructions do MCP e sobe SDK para 1.30.0"
```

---

### Task 2: Prompts MCP (registry + HTTP + stdio)

**Files:**
- Create: `backend/modules/ai/mcp/prompts.py`
- Modify: `backend/modules/ai/mcp/http/views.py` (capabilities + branches)
- Modify: `backend/modules/ai/mcp/tools/__init__.py` (`register_tools`)
- Test: `backend/modules/ai/mcp/tests/test_prompts.py`

**Interfaces:**
- Produces: `list_prompts() -> list[dict]` e `get_prompt(name: str, arguments: dict | None = None) -> dict | None`, com `messages` no formato MCP (`{"role": "user", "content": {"type": "text", "text": str}}`).

- [ ] **Step 1: Escrever o teste que falha**

Crie `backend/modules/ai/mcp/tests/test_prompts.py`:

```python
from django.test import SimpleTestCase

from modules.ai.mcp.http import views
from modules.ai.mcp.prompts import get_prompt, list_prompts


class TestPromptRegistry(SimpleTestCase):
    def test_lists_two_prompts(self):
        names = [prompt["name"] for prompt in list_prompts()]
        self.assertEqual(names, ["resumo_mensal", "onde_cortar_gastos"])

    def test_resumo_mensal_embeds_month(self):
        payload = get_prompt("resumo_mensal", {"mes": "2026-09"})

        text = payload["messages"][0]["content"]["text"]
        self.assertIn("2026-09", text)
        self.assertIn("summarize_spending", text)

    def test_resumo_mensal_without_month(self):
        payload = get_prompt("resumo_mensal", {})

        self.assertIn("mês corrente", payload["messages"][0]["content"]["text"])

    def test_unknown_prompt_returns_none(self):
        self.assertIsNone(get_prompt("nao_existe", {}))


class TestPromptDispatch(SimpleTestCase):
    def test_initialize_advertises_prompts_capability(self):
        response = views._dispatch(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize"}, user_id=1
        )
        self.assertIn("prompts", response["result"]["capabilities"])

    def test_prompts_list(self):
        response = views._dispatch(
            {"jsonrpc": "2.0", "id": 2, "method": "prompts/list"}, user_id=1
        )
        self.assertEqual(len(response["result"]["prompts"]), 2)

    def test_prompts_get(self):
        response = views._dispatch(
            {"jsonrpc": "2.0", "id": 3, "method": "prompts/get",
             "params": {"name": "resumo_mensal", "arguments": {"mes": "2026-09"}}},
            user_id=1,
        )
        self.assertIn("2026-09", response["result"]["messages"][0]["content"]["text"])

    def test_prompts_get_unknown(self):
        response = views._dispatch(
            {"jsonrpc": "2.0", "id": 4, "method": "prompts/get",
             "params": {"name": "nao_existe"}},
            user_id=1,
        )
        self.assertEqual(response["error"]["code"], -32602)
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/test_prompts.py -q
```

Esperado: FAIL com `ModuleNotFoundError: modules.ai.mcp.prompts`.

- [ ] **Step 3: Implementar `prompts.py`**

Crie `backend/modules/ai/mcp/prompts.py`:

```python
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


def list_prompts() -> list[dict]:
    return PROMPTS


def get_prompt(name: str, arguments: dict | None = None) -> dict | None:
    arguments = arguments or {}
    if name == "resumo_mensal":
        mes = (arguments.get("mes") or "").strip()
        if mes:
            texto = (
                f"Faça um resumo dos meus gastos de {mes}. "
                f"Use summarize_spending com due_month={mes} e group_by=category para {mes} "
                "e também para o mês anterior, e compare. Apresente o total do mês, "
                "as categorias que mais pesaram e a variação em relação ao mês anterior."
            )
        else:
            texto = (
                "Faça um resumo dos meus gastos do mês corrente. "
                "Use summarize_spending (sem due_month) com group_by=category para este mês "
                "e também para o mês anterior, e compare. Apresente o total do mês, "
                "as categorias que mais pesaram e a variação em relação ao mês anterior."
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
```

- [ ] **Step 4: Ligar no HTTP**

Em `backend/modules/ai/mcp/http/views.py`, importe `from modules.ai.mcp.prompts import get_prompt, list_prompts` e adicione as capabilities e os branches (antes do fallback de método desconhecido):

```python
            "capabilities": {
                "tools": {"listChanged": False},
                "prompts": {"listChanged": False},
            },
```

```python
    if method == "prompts/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"prompts": list_prompts()}}
    if method == "prompts/get":
        params = payload.get("params") or {}
        prompt = get_prompt(params.get("name"), params.get("arguments"))
        if prompt is None:
            return {
                "jsonrpc": "2.0", "id": rid,
                "error": {"code": -32602, "message": f"prompt não encontrado: {params.get('name')!r}"},
            }
        return {"jsonrpc": "2.0", "id": rid, "result": prompt}
```

- [ ] **Step 5: Ligar no stdio**

Em `backend/modules/ai/mcp/tools/__init__.py`, no topo, importe os tipos e o registry:

```python
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
)

from modules.ai.mcp.prompts import get_prompt as build_prompt
from modules.ai.mcp.prompts import list_prompts
```

e no fim de `register_tools`, adicione:

```python
    @server.list_prompts()
    async def handle_list_prompts() -> list[Prompt]:
        return [
            Prompt(
                name=prompt["name"],
                description=prompt["description"],
                arguments=[PromptArgument(**argument) for argument in prompt["arguments"]],
            )
            for prompt in list_prompts()
        ]

    @server.get_prompt()
    async def handle_get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
        payload = build_prompt(name, arguments)
        if payload is None:
            raise ValueError(f"prompt não encontrado: {name!r}")
        return GetPromptResult(
            description=payload["description"],
            messages=[
                PromptMessage(
                    role=message["role"],
                    content=TextContent(type="text", text=message["content"]["text"]),
                )
                for message in payload["messages"]
            ],
        )
```

- [ ] **Step 6: Rodar os testes**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/ -q
```

Esperado: `34 passed` (26 + 8 novos).

- [ ] **Step 7: Commit**

```bash
git add backend/modules/ai/mcp/prompts.py backend/modules/ai/mcp/http/views.py backend/modules/ai/mcp/tools/__init__.py backend/modules/ai/mcp/tests/test_prompts.py
git commit -m "feat: adiciona prompts do MCP nos dois transportes"
```

---

### Task 3: Registry de dispatch + erros acionáveis

**Files:**
- Modify: `backend/modules/ai/mcp/exceptions/mcp.py`
- Modify: `backend/modules/ai/mcp/exceptions/__init__.py`
- Modify: `backend/modules/ai/mcp/tools/__init__.py:166-231`
- Test: `backend/modules/ai/mcp/tests/test_dispatch_registry.py`

**Interfaces:**
- Produces: `InvalidCategoryError` (`INVALID_CATEGORY`), `InvalidDateError` (`INVALID_DATE`), `InvalidParamError` (`INVALID_PARAM`) em `modules.ai.mcp.exceptions`; `HANDLERS: dict[str, Callable]` em `modules.ai.mcp.tools`; `dispatch_tool` mantém assinatura e passa a incluir `available_tools` no erro `UNKNOWN_TOOL`.

- [ ] **Step 1: Escrever o teste que falha**

Crie `backend/modules/ai/mcp/tests/test_dispatch_registry.py`:

```python
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from modules.ai.mcp.exceptions import InvalidDateError
from modules.ai.mcp.tools import HANDLERS, TOOLS, dispatch_tool


class TestDispatchRegistry(SimpleTestCase):
    def test_every_tool_has_a_handler(self):
        self.assertEqual(
            sorted(tool["name"] for tool in TOOLS),
            sorted(HANDLERS),
        )

    def test_unknown_tool_lists_available(self):
        result = dispatch_tool("nao_existe", {}, Mock(), user_id=7)

        self.assertEqual(result["error"]["code"], "UNKNOWN_TOOL")
        self.assertIn("list_transactions", result["error"]["available_tools"])

    def test_mcp_error_maps_stable_code(self):
        def boom(arguments, container, user_id):
            raise InvalidDateError("data inválida")

        with patch.dict(HANDLERS, {"boom": boom}):
            result = dispatch_tool("boom", {}, Mock(), user_id=7)

        self.assertEqual(result["error"]["code"], "INVALID_DATE")
        self.assertEqual(result["error"]["message"], "data inválida")

    def test_wraps_unexpected_errors(self):
        def boom(arguments, container, user_id):
            raise Exception("boom")

        with patch.dict(HANDLERS, {"boom": boom}):
            result = dispatch_tool("boom", {}, Mock(), user_id=7)

        self.assertEqual(result["error"]["code"], "TOOL_ERROR")
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/test_dispatch_registry.py -q
```

Esperado: FAIL com `ImportError` (`InvalidDateError`) e `HANDLERS`.

- [ ] **Step 3: Adicionar as exceções**

Em `backend/modules/ai/mcp/exceptions/mcp.py`, ao final:

```python
class InvalidCategoryError(MCPError):
    code = "INVALID_CATEGORY"


class InvalidDateError(MCPError):
    code = "INVALID_DATE"


class InvalidParamError(MCPError):
    code = "INVALID_PARAM"
```

Em `backend/modules/ai/mcp/exceptions/__init__.py`:

```python
from modules.ai.mcp.exceptions.mcp import (
    InvalidCategoryError,
    InvalidDateError,
    InvalidParamError,
    MCPError,
)

__all__ = [
    "MCPError",
    "InvalidCategoryError",
    "InvalidDateError",
    "InvalidParamError",
]
```

- [ ] **Step 4: Trocar o if-chain por registry**

Em `backend/modules/ai/mcp/tools/__init__.py`, importe `from modules.ai.mcp.exceptions import MCPError` e substitua o corpo de `dispatch_tool` por um registry declarativo (mantendo os handlers existentes):

```python
HANDLERS = {
    "list_transactions": lambda arguments, container, user_id: transactions.call_list_transactions(
        arguments=arguments,
        use_case=container.transactions_container().list_transactions_use_case(),
        user_id=user_id,
    ),
    "get_transaction": lambda arguments, container, user_id: transactions.call_get_transaction(
        arguments=arguments,
        use_case=container.transactions_container().get_transaction_use_case(),
        user_id=user_id,
    ),
    "create_transaction": lambda arguments, container, user_id: transactions.call_create_transaction(
        arguments=arguments,
        use_case=container.transactions_container().create_transaction_use_case(),
        quick_add_use_case=container.transactions_container().quick_add_transaction_use_case(),
        user_id=user_id,
    ),
    "update_transaction": lambda arguments, container, user_id: transactions.call_update_transaction(
        arguments=arguments,
        use_case=container.transactions_container().update_transaction_use_case(),
        user_id=user_id,
    ),
    "create_sub_transaction": lambda arguments, container, user_id: transactions.call_create_sub_transaction(
        arguments=arguments,
        use_case=container.transactions_container().create_sub_transaction_use_case(),
        user_id=user_id,
    ),
    "update_sub_transaction": lambda arguments, container, user_id: transactions.call_update_sub_transaction(
        arguments=arguments,
        use_case=container.transactions_container().update_sub_transaction_use_case(),
        user_id=user_id,
    ),
    "list_enums": lambda arguments, container, user_id: call_list_enums(
        use_case=container.list_enums_use_case(),
    ),
    "get_projection": lambda arguments, container, user_id: transactions.call_get_projection(
        arguments=arguments,
        use_case=container.planning_container().projection_use_case(),
        user_id=user_id,
    ),
    "set_goals": lambda arguments, container, user_id: transactions.call_set_goals(
        arguments=arguments,
        update_profile_use_case=container.userdata_container().update_profile_use_case(),
        profile_repository=container.planning_container().profile_repository(),
        user_id=user_id,
    ),
}


def dispatch_tool(name: str, arguments: dict, container: MCPContainer, user_id: int) -> dict:
    handler = HANDLERS.get(name)
    if handler is None:
        return {
            "error": {
                "code": "UNKNOWN_TOOL",
                "message": f"unknown tool: {name}",
                "available_tools": sorted(HANDLERS),
            }
        }
    try:
        return handler(arguments=arguments, container=container, user_id=user_id)
    except MCPError as exc:
        return {"error": {"code": exc.code, "message": str(exc)}}
    except Exception as exc:  # noqa: BLE001 - surfaced to the agent as tool error
        logger.info("mcp.tool_error tool=%s error=%s", name, exc)
        return {"error": {"code": "TOOL_ERROR", "message": str(exc)}}
```

- [ ] **Step 5: Rodar a suíte do MCP**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/ -q
```

Esperado: `38 passed` (34 + 4 novos). Os testes antigos de `TestDispatchTool` continuam passando.

- [ ] **Step 6: Commit**

```bash
git add backend/modules/ai/mcp/exceptions backend/modules/ai/mcp/tools/__init__.py backend/modules/ai/mcp/tests/test_dispatch_registry.py
git commit -m "refactor: troca if-chain do dispatch por registry com erros acionáveis"
```

---

### Task 4: Helpers de categoria e data

**Files:**
- Create: `backend/modules/ai/mcp/categories.py`
- Create: `backend/modules/ai/mcp/dates.py`
- Test: `backend/modules/ai/mcp/tests/test_categories.py`
- Test: `backend/modules/ai/mcp/tests/test_dates.py`

**Interfaces:**
- Produces: `resolve_category(value) -> str | None` (levanta `InvalidCategoryError`); `with_category_slug(data: dict) -> dict`; `enrich_transaction(data: dict) -> dict`; `parse_month(value) -> tuple[int, int]`; `validate_date(value, field) -> str` (levanta `InvalidDateError`).

- [ ] **Step 1: Escrever os testes que falham**

Crie `backend/modules/ai/mcp/tests/test_categories.py`:

```python
from django.test import SimpleTestCase

from modules.ai.mcp.categories import enrich_transaction, resolve_category, with_category_slug
from modules.ai.mcp.exceptions import InvalidCategoryError


class TestResolveCategory(SimpleTestCase):
    def test_accepts_slug(self):
        self.assertEqual(resolve_category("transport_fuel"), "transport_fuel")

    def test_accepts_label(self):
        self.assertEqual(resolve_category("Transporte - Combustível"), "transport_fuel")

    def test_none_passthrough(self):
        self.assertIsNone(resolve_category(None))

    def test_invalid_raises_actionable_error(self):
        with self.assertRaises(InvalidCategoryError) as ctx:
            resolve_category("nao_existe")

        self.assertEqual(ctx.exception.code, "INVALID_CATEGORY")
        self.assertIn("list_enums", str(ctx.exception))


class TestEnrichCategorySlug(SimpleTestCase):
    def test_adds_slug_from_label(self):
        data = {"category": "Transporte - Combustível"}
        self.assertEqual(with_category_slug(data)["category_slug"], "transport_fuel")

    def test_unknown_label_becomes_none(self):
        self.assertEqual(with_category_slug({"category": "Nada"})["category_slug"], None)

    def test_enriches_transaction_and_subs(self):
        data = {
            "category": "Cartão de Crédito",
            "sub_transactions": [{"category": "Transporte - Combustível"}],
        }
        enriched = enrich_transaction(data)
        self.assertEqual(enriched["category_slug"], "credit_card")
        self.assertEqual(enriched["sub_transactions"][0]["category_slug"], "transport_fuel")
```

Crie `backend/modules/ai/mcp/tests/test_dates.py`:

```python
from django.test import SimpleTestCase

from modules.ai.mcp.dates import parse_month, validate_date
from modules.ai.mcp.exceptions import InvalidDateError


class TestParseMonth(SimpleTestCase):
    def test_parses(self):
        self.assertEqual(parse_month("2026-10"), (2026, 10))

    def test_invalid_raises(self):
        with self.assertRaises(InvalidDateError) as ctx:
            parse_month("2026-13")
        self.assertEqual(ctx.exception.code, "INVALID_DATE")
        self.assertIn("YYYY-MM", str(ctx.exception))


class TestValidateDate(SimpleTestCase):
    def test_normalizes(self):
        self.assertEqual(validate_date("2026-10-01", "due_start"), "2026-10-01")

    def test_invalid_raises(self):
        with self.assertRaises(InvalidDateError) as ctx:
            validate_date("01/10/2026", "due_start")
        self.assertIn("due_start", str(ctx.exception))
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/test_categories.py modules/ai/mcp/tests/test_dates.py -q
```

Esperado: FAIL com `ModuleNotFoundError`.

- [ ] **Step 3: Implementar `categories.py`**

```python
from modules.ai.mcp.exceptions import InvalidCategoryError
from modules.transactions.types import TransactionCategory


def _find_category(value: str):
    return TransactionCategory.get_by_name(value) or TransactionCategory.get_by_attribute_value(value, "value")


def resolve_category(value: str | None) -> str | None:
    if value is None:
        return None
    item = _find_category(str(value).strip())
    if item is None:
        raise InvalidCategoryError(
            f"categoria inválida: {value!r}. Use list_enums para ver os slugs válidos "
            "(ex.: transport_fuel)."
        )
    return item.name


def with_category_slug(data: dict) -> dict:
    label = data.get("category")
    item = TransactionCategory.get_by_attribute_value(label, "value") if label else None
    data["category_slug"] = item.name if item else None
    return data


def enrich_transaction(data: dict) -> dict:
    with_category_slug(data)
    for sub_transaction in data.get("sub_transactions") or []:
        with_category_slug(sub_transaction)
    return data
```

- [ ] **Step 4: Implementar `dates.py`**

```python
from datetime import date

from modules.ai.mcp.exceptions import InvalidDateError


def parse_month(value: str) -> tuple[int, int]:
    try:
        year, month = str(value).split("-")
        year, month = int(year), int(month)
    except (ValueError, AttributeError):
        raise InvalidDateError(f"mês inválido: {value!r}. Use YYYY-MM (ex.: 2026-10).")
    if not 1 <= month <= 12:
        raise InvalidDateError(f"mês inválido: {value!r}. Use YYYY-MM (ex.: 2026-10).")
    return year, month


def validate_date(value: str, field: str) -> str:
    try:
        return date.fromisoformat(str(value)).isoformat()
    except ValueError:
        raise InvalidDateError(
            f"{field} inválida: {value!r}. Use YYYY-MM-DD (ex.: 2026-10-01)."
        )
```

- [ ] **Step 5: Rodar os testes**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/ -q
```

Esperado: `49 passed` (38 + 11 novos).

- [ ] **Step 6: Commit**

```bash
git add backend/modules/ai/mcp/categories.py backend/modules/ai/mcp/dates.py backend/modules/ai/mcp/tests/test_categories.py backend/modules/ai/mcp/tests/test_dates.py
git commit -m "feat: adiciona helpers de categoria e data do MCP"
```

---

### Task 5: Recontrato das tools existentes (due_*, categorias e subtransações)

**Files:**
- Modify: `backend/modules/transactions/repositories/transaction.py:42-44`
- Modify: `backend/modules/transactions/use_cases/transaction/list.py`
- Modify: `backend/modules/transactions/container.py:173-177`
- Modify: `backend/modules/ai/mcp/tools/transactions.py:4-80`
- Modify: `backend/modules/ai/mcp/tools/__init__.py` (schema `list_transactions`)
- Test: `backend/modules/transactions/tests/test_transaction_repository_search.py` (novo)
- Test: `backend/modules/transactions/tests/test_list_transaction_use_case.py` (atualizar + hidratação)
- Test: `backend/modules/ai/mcp/tests/test_transactions_tools.py` (atualizar `TestListTransactionsTool`)

**Interfaces:**
- Consumes: `resolve_category`, `enrich_transaction`, `parse_month`, `validate_date` (Task 4).
- Produces: `TransactionRepository.filter(filters)` passa a tratar a chave `search` (OR identifier/subs + `distinct`); `ListTransactionsUseCase.execute(filters, include_subtransactions=False)`; handler `call_list_transactions` com parâmetros `due_month`/`due_start`/`due_end`/`include_subtransactions`.

- [ ] **Step 1: Escrever o teste de repositório que falha**

Crie `backend/modules/transactions/tests/test_transaction_repository_search.py`:

```python
from django.test import TestCase

from modules.transactions.factories import TransactionFactory
from modules.transactions.models import SubTransaction, Transaction
from modules.transactions.repositories import TransactionRepository
from modules.userdata.models import User


class TestTransactionRepositorySearch(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="search@test.com", password="x")
        self.repository = TransactionRepository(
            model=Transaction, transaction_factory=TransactionFactory()
        )
        self.bill = Transaction.objects.create(
            user=self.user,
            due_date="2026-10-08",
            total_amount="500.00",
            transaction_identifier="Fatura Nubank 10/2026",
            transaction_type="outgoing",
            category="credit_card",
        )
        SubTransaction.objects.create(
            transaction=self.bill,
            date="2026-09-02",
            description="POSTO PALMEIRAL",
            amount="100.00",
            category="transport_fuel",
        )
        SubTransaction.objects.create(
            transaction=self.bill,
            date="2026-09-05",
            description="POSTO PALMEIRAL",
            amount="100.00",
            category="transport_fuel",
        )

    def test_search_matches_sub_description_once(self):
        result = self.repository.filter({"user_id": self.user.id, "search": "posto"})

        self.assertEqual([transaction.id for transaction in result], [self.bill.id])

    def test_search_still_matches_identifier(self):
        result = self.repository.filter({"user_id": self.user.id, "search": "nubank"})

        self.assertEqual([transaction.id for transaction in result], [self.bill.id])
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/transactions/tests/test_transaction_repository_search.py -q
```

Esperado: FAIL em `test_search_matches_sub_description_once` (hoje `search` não existe como chave e estoura `FieldError`).

- [ ] **Step 3: Implementar o `search` no repositório**

Em `backend/modules/transactions/repositories/transaction.py`, importe `Q` e ajuste `filter`:

```python
from django.db.models import Case, When, Value, BooleanField, Exists, OuterRef, Q
```

```python
    def filter(self, filters: dict) -> list["TransactionDomain"]:
        filters = dict(filters)
        search = filters.pop("search", None)
        queryset = self.queryset
        if search:
            queryset = queryset.filter(
                Q(transaction_identifier__icontains=search)
                | Q(sub_transactions__description__icontains=search)
            ).distinct()
        queryset = self._annotate_subtransactions_paid(queryset.filter(**filters))
        return [self.transaction_factory.build_from_model(transaction) for transaction in queryset]
```

- [ ] **Step 4: Rodar o teste de repositório**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/transactions/tests/test_transaction_repository_search.py -q
```

Esperado: `2 passed`.

- [ ] **Step 5: Atualizar o use case (hidratação) e o provider**

Em `backend/modules/transactions/use_cases/transaction/list.py`:

```python
class ListTransactionsUseCase:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        transaction_serializer: TransactionSerializer,
        sub_transaction_repository: SubTransactionRepository,
    ):
        self.transaction_repository = transaction_repository
        self.transaction_serializer = transaction_serializer
        self.sub_transaction_repository = sub_transaction_repository

    def execute(self, filters: ListTransactionsFilters = {}, include_subtransactions: bool = False) -> list[dict]:
        transactions = self.transaction_repository.filter(filters=filters)
        if include_subtransactions and transactions:
            sub_transactions = self.sub_transaction_repository.get_all_by_transaction_ids(
                [transaction.id for transaction in transactions]
            )
            grouped: dict[int, list] = {}
            for sub_transaction in sub_transactions:
                grouped.setdefault(sub_transaction.transaction.id, []).append(sub_transaction)
            for transaction in transactions:
                transaction.set_sub_transactions(grouped.get(transaction.id, []))
        return [self.transaction_serializer.serialize(transaction) for transaction in transactions]
```

Importe `SubTransactionRepository` no topo do arquivo. Em `backend/modules/transactions/container.py`, no provider `list_transactions_use_case`, adicione:

```python
        sub_transaction_repository=sub_transaction_repository,
```

- [ ] **Step 6: Atualizar os testes do use case**

Em `backend/modules/transactions/tests/test_list_transaction_use_case.py`, no `setUp`:

```python
        self.mock_sub_transaction_repository = Mock()

        self.use_case = ListTransactionsUseCase(
            transaction_repository=self.mock_transaction_repository,
            transaction_serializer=self.mock_transaction_serializer,
            sub_transaction_repository=self.mock_sub_transaction_repository,
        )
```

E adicione o teste de hidratação em lote:

```python
    def test_include_subtransactions_hydrates_in_batch(self):
        transaction = TransactionDomain(
            id=1,
            due_date="2026-10-08",
            total_amount=100.00,
            transaction_identifier="Fatura Nubank 10/2026",
            transaction_type="outgoing",
            user_id=1,
        )
        sub_transaction = Mock(transaction=Mock(id=1), id=10)
        self.mock_transaction_repository.filter.return_value = [transaction]
        self.mock_sub_transaction_repository.get_all_by_transaction_ids.return_value = [sub_transaction]
        self.mock_transaction_serializer.serialize.return_value = {"id": 1}

        self.use_case.execute({"user_id": 1}, include_subtransactions=True)

        self.mock_sub_transaction_repository.get_all_by_transaction_ids.assert_called_once_with([1])
        self.assertEqual(transaction.sub_transactions, [sub_transaction])
```

E um teste com o serializer real garantindo que transação sem subs devolve lista vazia (nunca `null`):

```python
    def test_transaction_without_subs_serializes_empty_list(self):
        from modules.transactions.serializers import SubTransactionSerializer, TransactionSerializer

        serializer = TransactionSerializer(
            sub_transaction_serializer=SubTransactionSerializer(actor_serializer=Mock())
        )
        payload = serializer.serialize(
            TransactionDomain(
                id=9,
                due_date="2026-10-08",
                total_amount=100.00,
                transaction_identifier="Fatura C&A Pay 10/2026",
                transaction_type="outgoing",
                user_id=1,
            )
        )

        self.assertEqual(payload["sub_transactions"], [])
```

- [ ] **Step 7: Atualizar o handler e o schema do MCP**

Em `backend/modules/ai/mcp/tools/transactions.py`, importe os helpers e reescreva `call_list_transactions`:

```python
from modules.ai.mcp.categories import enrich_transaction, resolve_category
from modules.ai.mcp.dates import parse_month, validate_date
```

```python
def call_list_transactions(*, arguments: dict, use_case, user_id: int) -> dict:
    filters: dict[str, Any] = {"user_id": user_id}
    if arguments.get("due_month"):
        year, month = parse_month(arguments["due_month"])
        filters["due_date__year"] = year
        filters["due_date__month"] = month
    if arguments.get("due_start"):
        filters["due_date__gte"] = validate_date(arguments["due_start"], "due_start")
    if arguments.get("due_end"):
        filters["due_date__lte"] = validate_date(arguments["due_end"], "due_end")
    if arguments.get("transaction_type"):
        filters["transaction_type"] = arguments["transaction_type"]
    category = resolve_category(arguments.get("category"))
    if category:
        filters["category"] = category
    if arguments.get("paid") is not None:
        filters["paid_at__isnull"] = not bool(arguments["paid"])
    if arguments.get("search"):
        filters["search"] = arguments["search"]

    limit = min(int(arguments.get("limit") or 50), 200)
    transactions = use_case.execute(
        filters,
        include_subtransactions=bool(arguments.get("include_subtransactions")),
    )
    transactions = [enrich_transaction(transaction) for transaction in transactions[:limit]]
    return {"transactions": transactions, "count": len(transactions)}
```

No schema de `TOOLS` (`tools/__init__.py`), troque `start`/`end`/`month` por:

```python
                "due_start": {"type": "string", "description": "Vencimento a partir de (YYYY-MM-DD)"},
                "due_end": {"type": "string", "description": "Vencimento até (YYYY-MM-DD)"},
                "due_month": {"type": "string", "description": "Mês do vencimento/fatura (YYYY-MM)"},
                "include_subtransactions": {"type": "boolean", "description": "Inclui as compras (subtransações) de cada transação"},
```

e ajuste `LIST_TRANSACTIONS_DESCRIPTION` para:

```python
LIST_TRANSACTIONS_DESCRIPTION = (
    "Lista transações (faturas/documentos) do usuário. due_month (YYYY-MM) e "
    "due_start/due_end (YYYY-MM-DD) filtram o vencimento. search casa o "
    "identificador ou a descrição de subtransações. category aceita slug ou "
    "label (use list_enums). include_subtransactions=true devolve as compras de "
    "cada transação. limit padrão 50, máx 200. Valores em BRL."
)
```

No mesmo arquivo, aplique os helpers nas demais tools existentes. `get_transaction`:

```python
def call_get_transaction(*, arguments: dict, use_case, user_id: int) -> dict:
    return enrich_transaction(use_case.execute(arguments["transaction_id"], user_id))
```

`create_transaction` resolve a categoria nas duas rotas e enriquece o retorno:

```python
        data["category"] = resolve_category(arguments.get("category"))
        ...
        return enrich_transaction(quick_add_use_case.execute(data, user_id))
```

```python
    data = {
        ...
        "category": resolve_category(arguments.get("category")),
        ...
    }
    return enrich_transaction(use_case.execute(data))
```

`update_transaction`, `create_sub_transaction` e `update_sub_transaction` resolvem a categoria quando presente e enriquecem a saída:

```python
    if "category" in fields:
        fields["category"] = resolve_category(fields["category"])
    return enrich_transaction(use_case.execute(arguments["transaction_id"], fields))
```

```python
    if "category" in data:
        data["category"] = resolve_category(data["category"])
    return with_category_slug(use_case.execute(data, user_id))
```

```python
    if "category" in fields:
        fields["category"] = resolve_category(fields["category"])
    return with_category_slug(use_case.execute(arguments["sub_transaction_id"], fields, user_id))
```

Ajuste `CREATE_TRANSACTION_DESCRIPTION`, `UPDATE_TRANSACTION_DESCRIPTION`, `CREATE_SUB_TRANSACTION_DESCRIPTION` e `UPDATE_SUB_TRANSACTION_DESCRIPTION` para incluir "category aceita slug ou label (use list_enums)" e "valores em BRL".

- [ ] **Step 8: Atualizar os testes da tool**

Em `backend/modules/ai/mcp/tests/test_transactions_tools.py`, no `TestListTransactionsTool`, troque os argumentos e asserts:

```python
        result = transactions.call_list_transactions(
            arguments={
                "due_month": "2026-09",
                "transaction_type": "outgoing",
                "paid": False,
                "search": "padaria",
                "limit": 2,
            },
            use_case=use_case,
            user_id=7,
        )

        filters = use_case.execute.call_args[0][0]
        self.assertEqual(filters["user_id"], 7)
        self.assertEqual(filters["due_date__year"], 2026)
        self.assertEqual(filters["due_date__month"], 9)
        self.assertEqual(filters["transaction_type"], "outgoing")
        self.assertEqual(filters["paid_at__isnull"], True)
        self.assertEqual(filters["search"], "padaria")
        self.assertEqual(result["count"], 2)
        self.assertEqual(
            use_case.execute.call_args[1]["include_subtransactions"], False
        )
```

No `test_range_filters`:

```python
        transactions.call_list_transactions(
            arguments={"due_start": "2026-09-01", "due_end": "2026-09-30"},
            use_case=use_case,
            user_id=7,
        )

        filters = use_case.execute.call_args[0][0]
        self.assertEqual(filters["due_date__gte"], "2026-09-01")
        self.assertEqual(filters["due_date__lte"], "2026-09-30")
```

Adicione um teste de enrichment + flag:

```python
    def test_enriches_category_slug_and_forwards_flag(self):
        use_case = Mock()
        use_case.execute.return_value = [
            {"id": 1, "category": "Transporte - Combustível", "sub_transactions": [{"category": "Outros"}]}
        ]

        result = transactions.call_list_transactions(
            arguments={"include_subtransactions": True},
            use_case=use_case,
            user_id=7,
        )

        self.assertEqual(result["transactions"][0]["category_slug"], "transport_fuel")
        self.assertEqual(result["transactions"][0]["sub_transactions"][0]["category_slug"], "other")
        self.assertTrue(use_case.execute.call_args[1]["include_subtransactions"])
```

Ainda no mesmo arquivo, ajuste as asserções que quebram com o enrichment (`{"ok": True}` ganha `category_slug`):

- `TestGetTransactionTool.test_scopes_by_user`: troque `self.assertEqual(result, {"id": 10})` por `self.assertEqual(result["id"], 10)`.
- `TestCreateTransactionTool.test_routes_to_quick_add_when_payment_method_given`: troque `self.assertEqual(result, {"ok": True})` por `self.assertTrue(result["ok"])`.
- `TestDispatchTool.test_routes_list_transactions`: troque `self.assertEqual(result["transactions"], [{"id": 1}])` por `self.assertEqual(result["transactions"][0]["id"], 1)`.

Adicione os testes do enrichment e da resolução por label:

```python
class TestGetTransactionToolEnrichment(SimpleTestCase):
    def test_adds_category_slug(self):
        use_case = Mock()
        use_case.execute.return_value = {
            "id": 10,
            "category": "Cartão de Crédito",
            "sub_transactions": [{"category": "Transporte - Combustível"}],
        }

        result = transactions.call_get_transaction(
            arguments={"transaction_id": 10}, use_case=use_case, user_id=7
        )

        self.assertEqual(result["category_slug"], "credit_card")
        self.assertEqual(result["sub_transactions"][0]["category_slug"], "transport_fuel")


class TestCreateTransactionCategoryLabel(SimpleTestCase):
    def test_resolves_label_to_slug(self):
        quick_add = Mock()
        quick_add.execute.return_value = {"id": 1, "category": "Transporte - Combustível"}

        transactions.call_create_transaction(
            arguments={
                "transaction_identifier": "Posto",
                "total_amount": "100",
                "due_date": "2026-10-01",
                "payment_method": "cash",
                "category": "Transporte - Combustível",
            },
            use_case=Mock(),
            quick_add_use_case=quick_add,
            user_id=7,
        )

        self.assertEqual(quick_add.execute.call_args[0][0]["category"], "transport_fuel")
```

- [ ] **Step 9: Rodar as suítes**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/ modules/transactions/tests/ -q
```

Esperado: tudo verde (as demais tools ainda não usam os helpers).

- [ ] **Step 10: Commit**

```bash
git add backend/modules/transactions/repositories/transaction.py backend/modules/transactions/use_cases/transaction/list.py backend/modules/transactions/container.py backend/modules/ai/mcp/tools/transactions.py backend/modules/ai/mcp/tools/__init__.py backend/modules/transactions/tests/test_transaction_repository_search.py backend/modules/transactions/tests/test_list_transaction_use_case.py backend/modules/ai/mcp/tests/test_transactions_tools.py
git commit -m "feat: recontrata tools existentes do MCP (due_*, categorias e subtransações)"
```

---

### Task 6: Tool `list_sub_transactions`

**Files:**
- Modify: `backend/modules/transactions/repositories/sub_transaction.py` (novo `filter`)
- Modify: `backend/modules/transactions/use_cases/sub_transaction/list.py` (filtros)
- Modify: `backend/modules/transactions/serializers/sub_transaction.py:26-40` (campo `card_id`)
- Create: `backend/modules/ai/mcp/tools/sub_transactions.py`
- Modify: `backend/modules/ai/mcp/tools/__init__.py` (TOOLS + HANDLERS)
- Test: `backend/modules/transactions/tests/test_sub_transaction_repository_filter.py` (novo)
- Test: `backend/modules/transactions/tests/test_sub_transaction_serializer_card_id.py` (novo)
- Test: `backend/modules/ai/mcp/tests/test_sub_transactions_tool.py` (novo)

**Interfaces:**
- Consumes: `resolve_category`, `with_category_slug`, `parse_month`, `validate_date` (Task 4); `HANDLERS` (Task 3).
- Produces: `SubTransactionRepository.filter(user_id, filters)`; `ListSubTransactionsUseCase.execute(user_id, due_date=None, actor_id=None, filters=None)`; `SubTransactionSerializer.serialize` inclui `card_id`; tool `list_sub_transactions` com resposta `{"sub_transactions": [...], "count": N}`.

- [ ] **Step 1: Escrever os testes que falham**

Crie `backend/modules/transactions/tests/test_sub_transaction_repository_filter.py`:

```python
from django.test import TestCase

from modules.transactions.factories import SubTransactionFactory
from modules.transactions.models import SubTransaction, Transaction
from modules.transactions.repositories import SubTransactionRepository
from modules.userdata.models import User


class TestSubTransactionRepositoryFilter(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="subs@test.com", password="x")
        self.repository = SubTransactionRepository(
            model=SubTransaction, sub_transaction_factory=SubTransactionFactory()
        )
        self.bill = Transaction.objects.create(
            user=self.user,
            due_date="2026-10-08",
            total_amount="300.00",
            transaction_identifier="Fatura Inter 10/2026",
            transaction_type="outgoing",
            category="credit_card",
        )
        SubTransaction.objects.create(
            transaction=self.bill, date="2026-09-02", description="POSTO PALMEIRAL",
            amount="100.00", category="transport_fuel",
        )
        SubTransaction.objects.create(
            transaction=self.bill, date="2026-09-05", description="MERCADINHO",
            amount="200.00", category="food_grocery",
        )

    def test_filters_by_purchase_month_and_category(self):
        result = self.repository.filter(
            self.user.id,
            {"date__year": 2026, "date__month": 9, "category": "transport_fuel"},
        )

        self.assertEqual([sub.description for sub in result], ["POSTO PALMEIRAL"])

    def test_filters_by_parent_due_month_and_search(self):
        result = self.repository.filter(
            self.user.id,
            {"transaction__due_date__month": 10, "description__icontains": "merc"},
        )

        self.assertEqual([sub.description for sub in result], ["MERCADINHO"])
```

Crie `backend/modules/transactions/tests/test_sub_transaction_serializer_card_id.py`:

```python
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.transactions.domains import SubTransactionDomain, TransactionDomain
from modules.transactions.serializers import SubTransactionSerializer


class TestSubTransactionSerializerCardId(SimpleTestCase):
    def test_serialize_includes_parent_card_id(self):
        transaction = TransactionDomain(
            id=1,
            due_date="2026-10-08",
            total_amount="100.00",
            transaction_identifier="Fatura Nubank 10/2026",
            transaction_type="outgoing",
            category="credit_card",
            card_id=3,
        )
        sub_transaction = SubTransactionDomain(
            id=10,
            date="2026-09-02",
            description="POSTO PALMEIRAL",
            amount="100.00",
            transaction=transaction,
            category="transport_fuel",
        )

        payload = SubTransactionSerializer(actor_serializer=Mock()).serialize(sub_transaction)

        self.assertEqual(payload["card_id"], 3)
```

Crie `backend/modules/ai/mcp/tests/test_sub_transactions_tool.py`:

```python
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.exceptions import InvalidDateError
from modules.ai.mcp.tools.sub_transactions import call_list_sub_transactions


class TestListSubTransactionsTool(SimpleTestCase):
    def test_builds_filters_and_clamps_limit(self):
        use_case = Mock()
        use_case.execute.return_value = [
            {"id": 1, "category": "Transporte - Combustível"},
            {"id": 2, "category": "Outros"},
        ]

        result = call_list_sub_transactions(
            arguments={
                "purchase_month": "2026-09",
                "due_month": "2026-10",
                "category": "Transporte - Combustível",
                "search": "posto",
                "limit": 1,
            },
            use_case=use_case,
            user_id=7,
        )

        filters = use_case.execute.call_args[1]["filters"]
        self.assertEqual(filters["date__year"], 2026)
        self.assertEqual(filters["date__month"], 9)
        self.assertEqual(filters["transaction__due_date__month"], 10)
        self.assertEqual(filters["category"], "transport_fuel")
        self.assertEqual(filters["description__icontains"], "posto")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["sub_transactions"][0]["category_slug"], "transport_fuel")

    def test_invalid_date_raises(self):
        with self.assertRaises(InvalidDateError):
            call_list_sub_transactions(
                arguments={"purchase_month": "2026-13"},
                use_case=Mock(),
                user_id=7,
            )
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/transactions/tests/test_sub_transaction_repository_filter.py modules/transactions/tests/test_sub_transaction_serializer_card_id.py modules/ai/mcp/tests/test_sub_transactions_tool.py -q
```

Esperado: FAIL (`AttributeError: 'SubTransactionRepository' object has no attribute 'filter'`, `KeyError: 'card_id'`, `ModuleNotFoundError`).

- [ ] **Step 3: Implementar repositório, use case e serializer**

Em `backend/modules/transactions/repositories/sub_transaction.py`, adicione:

```python
    def filter(self, user_id: int, filters: dict = {}) -> list["SubTransactionDomain"]:
        sub_transaction_instances = self.queryset.filter(transaction__user_id=user_id, **filters)
        return [
            self.sub_transaction_factory.build_from_model(sub_transaction_instance)
            for sub_transaction_instance in sub_transaction_instances
        ]
```

Em `backend/modules/transactions/use_cases/sub_transaction/list.py`:

```python
    def execute(self, user_id: int, due_date: str = None, actor_id: str = None, filters: dict = None) -> list[dict]:
        if filters is not None:
            sub_transactions = self.sub_transaction_repository.filter(user_id, filters)
        else:
            sub_transactions = self.sub_transaction_repository.get_all(user_id, due_date, actor_id)
        return [self.sub_transaction_serializer.serialize(sub_transaction) for sub_transaction in sub_transactions]
```

Em `backend/modules/transactions/serializers/sub_transaction.py`, adicione ao dict de `serialize` (logo após `transaction_identifier`):

```python
            "card_id": sub_transaction.transaction.card_id,
```

- [ ] **Step 4: Rodar os testes de domínio**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/transactions/tests/test_sub_transaction_repository_filter.py modules/transactions/tests/test_sub_transaction_serializer_card_id.py -q
```

Esperado: `3 passed`.

- [ ] **Step 5: Implementar a tool**

Crie `backend/modules/ai/mcp/tools/sub_transactions.py`:

```python
from typing import Any

from modules.ai.mcp.categories import resolve_category, with_category_slug
from modules.ai.mcp.dates import parse_month, validate_date


LIST_SUB_TRANSACTIONS_DESCRIPTION = (
    "Lista compras (subtransações) de forma plana e filtrável. purchase_month "
    "(YYYY-MM) e purchase_start/purchase_end (YYYY-MM-DD) filtram a data da "
    "compra; due_month e due_start/due_end filtram o vencimento da fatura pai. "
    "category aceita slug ou label; search casa a descrição; transaction_id e "
    "actor_id restringem à fatura/ator. limit padrão 100, máx 200. Valores em BRL."
)


def call_list_sub_transactions(*, arguments: dict, use_case, user_id: int) -> dict:
    filters: dict[str, Any] = {}
    if arguments.get("purchase_month"):
        year, month = parse_month(arguments["purchase_month"])
        filters["date__year"] = year
        filters["date__month"] = month
    if arguments.get("purchase_start"):
        filters["date__gte"] = validate_date(arguments["purchase_start"], "purchase_start")
    if arguments.get("purchase_end"):
        filters["date__lte"] = validate_date(arguments["purchase_end"], "purchase_end")
    if arguments.get("due_month"):
        year, month = parse_month(arguments["due_month"])
        filters["transaction__due_date__year"] = year
        filters["transaction__due_date__month"] = month
    if arguments.get("due_start"):
        filters["transaction__due_date__gte"] = validate_date(arguments["due_start"], "due_start")
    if arguments.get("due_end"):
        filters["transaction__due_date__lte"] = validate_date(arguments["due_end"], "due_end")
    category = resolve_category(arguments.get("category"))
    if category:
        filters["category"] = category
    if arguments.get("search"):
        filters["description__icontains"] = arguments["search"]
    if arguments.get("transaction_id"):
        filters["transaction_id"] = arguments["transaction_id"]
    if arguments.get("actor_id"):
        filters["actor_id"] = arguments["actor_id"]

    limit = min(int(arguments.get("limit") or 100), 200)
    sub_transactions = use_case.execute(user_id, filters=filters)[:limit]
    sub_transactions = [with_category_slug(sub_transaction) for sub_transaction in sub_transactions]
    return {"sub_transactions": sub_transactions, "count": len(sub_transactions)}
```

Em `backend/modules/ai/mcp/tools/__init__.py`, importe `from modules.ai.mcp.tools import sub_transactions` e adicione em `TOOLS`:

```python
    {
        "name": "list_sub_transactions",
        "description": sub_transactions.LIST_SUB_TRANSACTIONS_DESCRIPTION,
        "inputSchema": {
            "type": "object",
            "properties": {
                "purchase_month": {"type": "string", "description": "Mês da compra (YYYY-MM)"},
                "purchase_start": {"type": "string", "description": "Compra a partir de (YYYY-MM-DD)"},
                "purchase_end": {"type": "string", "description": "Compra até (YYYY-MM-DD)"},
                "due_month": {"type": "string", "description": "Mês do vencimento da fatura pai (YYYY-MM)"},
                "due_start": {"type": "string", "description": "Vencimento a partir de (YYYY-MM-DD)"},
                "due_end": {"type": "string", "description": "Vencimento até (YYYY-MM-DD)"},
                "category": {"type": "string"},
                "search": {"type": "string", "description": "Trecho da descrição da compra"},
                "transaction_id": {"type": "integer"},
                "actor_id": {"type": "integer"},
                "limit": {"type": "integer", "maximum": 200},
            },
        },
    },
```

e em `HANDLERS`:

```python
    "list_sub_transactions": lambda arguments, container, user_id: sub_transactions.call_list_sub_transactions(
        arguments=arguments,
        use_case=container.transactions_container().list_sub_transactions_use_case(),
        user_id=user_id,
    ),
```

- [ ] **Step 6: Rodar as suítes**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/ modules/transactions/tests/ -q
```

Esperado: tudo verde.

- [ ] **Step 7: Commit**

```bash
git add backend/modules/transactions/repositories/sub_transaction.py backend/modules/transactions/use_cases/sub_transaction/list.py backend/modules/transactions/serializers/sub_transaction.py backend/modules/ai/mcp/tools/sub_transactions.py backend/modules/ai/mcp/tools/__init__.py backend/modules/transactions/tests/test_sub_transaction_repository_filter.py backend/modules/transactions/tests/test_sub_transaction_serializer_card_id.py backend/modules/ai/mcp/tests/test_sub_transactions_tool.py
git commit -m "feat: adiciona list_sub_transactions ao MCP"
```

---

### Task 7: Tool `summarize_spending`

**Files:**
- Create: `backend/modules/transactions/use_cases/transaction/summarize_spending.py`
- Modify: `backend/modules/transactions/use_cases/__init__.py` (export)
- Modify: `backend/modules/transactions/container.py` (provider)
- Create: `backend/modules/ai/mcp/tools/spending.py`
- Modify: `backend/modules/ai/mcp/tools/__init__.py` (TOOLS + HANDLERS)
- Test: `backend/modules/transactions/tests/test_summarize_spending_use_case.py` (novo)
- Test: `backend/modules/ai/mcp/tests/test_spending_tool.py` (novo)

**Interfaces:**
- Consumes: `resolve_category`, `parse_month`, `validate_date` (Task 4); `HANDLERS` (Task 3).
- Produces: `SummarizeSpendingUseCase.execute(user_id, filters) -> {"total": str, "count": int, "currency": "BRL", "groups": [...]}`; filtros aceitos: `due_date__year/month/gte/lte`, `purchase_month/start/end`, `category`, `search`, `transaction_type`, `group_by`; tool `summarize_spending`.

- [ ] **Step 1: Escrever os testes do use case que falham**

Crie `backend/modules/transactions/tests/test_summarize_spending_use_case.py`:

```python
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.transactions.domains import SubTransactionDomain, TransactionDomain
from modules.transactions.use_cases.transaction.summarize_spending import SummarizeSpendingUseCase


def build_use_case(transactions, sub_transactions, cards=None):
    transaction_repository = Mock()
    transaction_repository.filter.return_value = transactions
    sub_transaction_repository = Mock()
    sub_transaction_repository.get_all_by_transaction_ids.return_value = sub_transactions
    card_repository = Mock()
    card_repository.get_all.return_value = cards or []
    return SummarizeSpendingUseCase(
        transaction_repository=transaction_repository,
        sub_transaction_repository=sub_transaction_repository,
        card_repository=card_repository,
    )


def build_bill_with_subs():
    bill = TransactionDomain(
        id=1, due_date=date(2026, 10, 8), total_amount=Decimal("500.00"),
        transaction_identifier="Fatura Nubank 10/2026", transaction_type="outgoing",
        category="credit_card", card_id=1, user_id=7,
    )
    fuel = SubTransactionDomain(
        id=1, date=date(2026, 9, 2), description="POSTO", amount=Decimal("100.00"),
        transaction=bill, category="transport_fuel",
    )
    market = SubTransactionDomain(
        id=2, date=date(2026, 9, 5), description="MERCADO", amount=Decimal("400.00"),
        transaction=bill, category="food_grocery",
    )
    return bill, fuel, market


class TestSummarizeSpendingUseCase(SimpleTestCase):
    def test_card_bill_counts_subs_not_total(self):
        bill, fuel, market = build_bill_with_subs()
        use_case = build_use_case([bill], [fuel, market])

        result = use_case.execute(7, {"transaction_type": "outgoing"})

        self.assertEqual(result["total"], "500.00")
        self.assertEqual(result["count"], 2)

    def test_category_filter_does_not_leak_bill_total(self):
        bill, fuel, market = build_bill_with_subs()
        use_case = build_use_case([bill], [fuel, market])

        result = use_case.execute(7, {"category": "transport_fuel"})

        self.assertEqual(result["total"], "100.00")
        self.assertEqual(result["count"], 1)

    def test_standalone_transaction_counts_total_and_uses_due_date(self):
        pix = TransactionDomain(
            id=2, due_date=date(2026, 9, 20), total_amount=Decimal("50.00"),
            transaction_identifier="Posto via Pix", transaction_type="outgoing",
            category="transport_fuel", user_id=7,
        )
        use_case = build_use_case([pix], [])

        result = use_case.execute(7, {"purchase_month": "2026-09"})

        self.assertEqual(result["total"], "50.00")
        self.assertEqual(result["count"], 1)

    def test_group_by_category(self):
        bill, fuel, market = build_bill_with_subs()
        use_case = build_use_case([bill], [fuel, market])

        result = use_case.execute(7, {"group_by": "category"})

        groups = {group["key"]: group for group in result["groups"]}
        self.assertEqual(groups["food_grocery"]["total"], "400.00")
        self.assertEqual(groups["transport_fuel"]["label"], "Transporte - Combustível")

    def test_group_by_card(self):
        card = Mock(id=1, name="Nubank")
        bill, fuel, market = build_bill_with_subs()
        use_case = build_use_case([bill], [fuel, market], cards=[card])

        result = use_case.execute(7, {"group_by": "card"})

        self.assertEqual(result["groups"][0]["label"], "Nubank")

    def test_group_by_month(self):
        bill, fuel, market = build_bill_with_subs()
        use_case = build_use_case([bill], [fuel, market])

        result = use_case.execute(7, {"group_by": "month"})

        self.assertEqual(result["groups"][0]["key"], "2026-09")
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/transactions/tests/test_summarize_spending_use_case.py -q
```

Esperado: FAIL com `ModuleNotFoundError`.

- [ ] **Step 3: Implementar o use case**

Crie `backend/modules/transactions/use_cases/transaction/summarize_spending.py`:

```python
from decimal import Decimal

from modules.cards.repositories import CardRepository
from modules.transactions.repositories import SubTransactionRepository, TransactionRepository
from modules.transactions.types import TransactionCategory


class SummarizeSpendingUseCase:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        sub_transaction_repository: SubTransactionRepository,
        card_repository: CardRepository,
    ):
        self.transaction_repository = transaction_repository
        self.sub_transaction_repository = sub_transaction_repository
        self.card_repository = card_repository

    def execute(self, user_id: int, filters: dict = {}) -> dict:
        transaction_type = filters.get("transaction_type") or "outgoing"
        group_by = filters.get("group_by") or "none"
        due_filters = {key: value for key, value in filters.items() if key.startswith("due_date__")}
        purchase_filters = {key: value for key, value in filters.items() if key.startswith("purchase_")}
        category = filters.get("category")
        search = (filters.get("search") or "").strip().lower()

        transactions = self.transaction_repository.filter(
            {"user_id": user_id, "transaction_type": transaction_type, **due_filters}
        )
        sub_transactions = self.sub_transaction_repository.get_all_by_transaction_ids(
            [transaction.id for transaction in transactions]
        )
        subs_by_transaction: dict[int, list] = {}
        for sub_transaction in sub_transactions:
            subs_by_transaction.setdefault(sub_transaction.transaction.id, []).append(sub_transaction)

        cards = {card.id: card.name for card in self.card_repository.get_all(user_id)}

        items = []
        for transaction in transactions:
            transaction_subs = subs_by_transaction.get(transaction.id, [])
            if transaction_subs:
                for sub_transaction in transaction_subs:
                    if category and sub_transaction.category != category:
                        continue
                    if search and search not in (sub_transaction.description or "").lower():
                        continue
                    if not self._in_purchase_window(sub_transaction.date, purchase_filters):
                        continue
                    items.append({
                        "category": sub_transaction.category,
                        "card_id": transaction.card_id,
                        "date": sub_transaction.date,
                        "amount": Decimal(str(sub_transaction.amount)),
                    })
            else:
                if category and transaction.category != category:
                    continue
                if search and search not in (transaction.transaction_identifier or "").lower():
                    continue
                if not self._in_purchase_window(transaction.due_date, purchase_filters):
                    continue
                items.append({
                    "category": transaction.category,
                    "card_id": transaction.card_id,
                    "date": transaction.due_date,
                    "amount": Decimal(str(transaction.total_amount)),
                })

        total = sum((item["amount"] for item in items), Decimal("0"))
        return {
            "total": self._money(total),
            "count": len(items),
            "currency": "BRL",
            "groups": self._build_groups(items, group_by, cards),
        }

    def _in_purchase_window(self, value, filters: dict) -> bool:
        if not filters:
            return True
        value_str = str(value)
        if filters.get("purchase_month") and value_str[:7] != filters["purchase_month"]:
            return False
        if filters.get("purchase_start") and value_str < filters["purchase_start"]:
            return False
        if filters.get("purchase_end") and value_str > filters["purchase_end"]:
            return False
        return True

    def _build_groups(self, items: list[dict], group_by: str, cards: dict) -> list[dict]:
        if group_by == "none":
            return []
        buckets: dict = {}
        for item in items:
            if group_by == "category":
                key = item["category"] or TransactionCategory.OTHER.name
                label = getattr(TransactionCategory.get_by_name(key), "value", TransactionCategory.OTHER.value)
            elif group_by == "card":
                key = str(item["card_id"]) if item["card_id"] else "sem_cartao"
                label = cards.get(item["card_id"], "Sem cartão") if item["card_id"] else "Sem cartão"
            else:  # month
                key = str(item["date"])[:7]
                label = key
            bucket = buckets.setdefault(
                key, {"key": key, "label": label, "total": Decimal("0"), "count": 0}
            )
            bucket["total"] += item["amount"]
            bucket["count"] += 1
        groups = [
            {"key": bucket["key"], "label": bucket["label"], "total": self._money(bucket["total"]), "count": bucket["count"]}
            for bucket in buckets.values()
        ]
        return sorted(groups, key=lambda group: Decimal(group["total"]), reverse=True)

    @staticmethod
    def _money(value: Decimal) -> str:
        return str(value.quantize(Decimal("0.01")))
```

Em `backend/modules/transactions/use_cases/__init__.py`, adicione o import/export de `SummarizeSpendingUseCase` (mesmo padrão dos vizinhos) e em `backend/modules/transactions/container.py`:

```python
    summarize_spending_use_case = providers.Factory(
        SummarizeSpendingUseCase,
        transaction_repository=transaction_repository,
        sub_transaction_repository=sub_transaction_repository,
        card_repository=card_repository,
    )
```

(importe `SummarizeSpendingUseCase` na lista de use cases do container).

- [ ] **Step 4: Rodar o teste do use case**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/transactions/tests/test_summarize_spending_use_case.py -q
```

Esperado: `6 passed`.

- [ ] **Step 5: Implementar a tool**

Crie `backend/modules/ai/mcp/tools/spending.py`:

```python
from typing import Any

from modules.ai.mcp.categories import resolve_category
from modules.ai.mcp.dates import parse_month, validate_date
from modules.ai.mcp.exceptions import InvalidParamError


SUMMARIZE_SPENDING_DESCRIPTION = (
    "Soma gastos (ou entradas) com filtros e agrupamento no servidor — use para "
    "'quanto gastei com X'. due_* filtra o vencimento (fatura); purchase_* filtra "
    "a data da compra (subtransações; em transação sem subs vale o vencimento). "
    "Regra: fatura de cartão conta pelas subtransações (nunca pelo total), "
    "transação sem subs conta o total. group_by: none, category, card ou month. "
    "transaction_type padrão outgoing. Valores em BRL."
)

GROUP_BY_OPTIONS = ("none", "category", "card", "month")


def call_summarize_spending(*, arguments: dict, use_case, user_id: int) -> dict:
    filters: dict[str, Any] = {}
    if arguments.get("due_month"):
        year, month = parse_month(arguments["due_month"])
        filters["due_date__year"] = year
        filters["due_date__month"] = month
    if arguments.get("due_start"):
        filters["due_date__gte"] = validate_date(arguments["due_start"], "due_start")
    if arguments.get("due_end"):
        filters["due_date__lte"] = validate_date(arguments["due_end"], "due_end")
    if arguments.get("purchase_month"):
        parse_month(arguments["purchase_month"])
        filters["purchase_month"] = arguments["purchase_month"]
    if arguments.get("purchase_start"):
        filters["purchase_start"] = validate_date(arguments["purchase_start"], "purchase_start")
    if arguments.get("purchase_end"):
        filters["purchase_end"] = validate_date(arguments["purchase_end"], "purchase_end")
    category = resolve_category(arguments.get("category"))
    if category:
        filters["category"] = category
    if arguments.get("search"):
        filters["search"] = arguments["search"]
    filters["transaction_type"] = arguments.get("transaction_type") or "outgoing"

    group_by = arguments.get("group_by") or "none"
    if group_by not in GROUP_BY_OPTIONS:
        raise InvalidParamError(
            f"group_by inválido: {group_by!r}. Use um de: {', '.join(GROUP_BY_OPTIONS)}."
        )
    filters["group_by"] = group_by

    return use_case.execute(user_id, filters)
```

Em `backend/modules/ai/mcp/tools/__init__.py`, importe `from modules.ai.mcp.tools import spending` e adicione em `TOOLS`:

```python
    {
        "name": "summarize_spending",
        "description": spending.SUMMARIZE_SPENDING_DESCRIPTION,
        "inputSchema": {
            "type": "object",
            "properties": {
                "due_month": {"type": "string", "description": "Mês do vencimento/fatura (YYYY-MM)"},
                "due_start": {"type": "string", "description": "Vencimento a partir de (YYYY-MM-DD)"},
                "due_end": {"type": "string", "description": "Vencimento até (YYYY-MM-DD)"},
                "purchase_month": {"type": "string", "description": "Mês da compra (YYYY-MM)"},
                "purchase_start": {"type": "string", "description": "Compra a partir de (YYYY-MM-DD)"},
                "purchase_end": {"type": "string", "description": "Compra até (YYYY-MM-DD)"},
                "category": {"type": "string"},
                "search": {"type": "string"},
                "transaction_type": {"type": "string", "enum": ["incoming", "outgoing"]},
                "group_by": {"type": "string", "enum": ["none", "category", "card", "month"]},
            },
        },
    },
```

e em `HANDLERS`:

```python
    "summarize_spending": lambda arguments, container, user_id: spending.call_summarize_spending(
        arguments=arguments,
        use_case=container.transactions_container().summarize_spending_use_case(),
        user_id=user_id,
    ),
```

- [ ] **Step 6: Escrever o teste da tool**

Crie `backend/modules/ai/mcp/tests/test_spending_tool.py`:

```python
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.exceptions import InvalidParamError
from modules.ai.mcp.tools.spending import call_summarize_spending


class TestSummarizeSpendingTool(SimpleTestCase):
    def test_forwards_normalized_filters(self):
        use_case = Mock()
        use_case.execute.return_value = {"total": "100.00", "count": 1, "groups": []}

        result = call_summarize_spending(
            arguments={
                "due_month": "2026-10",
                "purchase_month": "2026-09",
                "category": "transport_fuel",
                "group_by": "category",
            },
            use_case=use_case,
            user_id=7,
        )

        filters = use_case.execute.call_args[0][1]
        self.assertEqual(filters["due_date__year"], 2026)
        self.assertEqual(filters["due_date__month"], 10)
        self.assertEqual(filters["purchase_month"], "2026-09")
        self.assertEqual(filters["category"], "transport_fuel")
        self.assertEqual(filters["transaction_type"], "outgoing")
        self.assertEqual(filters["group_by"], "category")
        self.assertEqual(result["total"], "100.00")

    def test_invalid_group_by_raises(self):
        with self.assertRaises(InvalidParamError):
            call_summarize_spending(
                arguments={"group_by": "planeta"},
                use_case=Mock(),
                user_id=7,
            )
```

- [ ] **Step 7: Rodar as suítes**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/ modules/transactions/tests/ -q
```

Esperado: tudo verde.

- [ ] **Step 8: Commit**

```bash
git add backend/modules/transactions/use_cases/transaction/summarize_spending.py backend/modules/transactions/use_cases/__init__.py backend/modules/transactions/container.py backend/modules/ai/mcp/tools/spending.py backend/modules/ai/mcp/tools/__init__.py backend/modules/transactions/tests/test_summarize_spending_use_case.py backend/modules/ai/mcp/tests/test_spending_tool.py
git commit -m "feat: adiciona summarize_spending ao MCP"
```

---

### Task 8: Tools `list_cards` e `list_actors`

**Files:**
- Modify: `backend/modules/ai/mcp/container.py` (cards_container)
- Create: `backend/modules/ai/mcp/tools/directory.py`
- Modify: `backend/modules/ai/mcp/tools/__init__.py` (TOOLS + HANDLERS)
- Test: `backend/modules/ai/mcp/tests/test_directory_tools.py`

**Interfaces:**
- Consumes: `CardsContainer` (`list_cards_use_case`) e `TransactionsContainer.list_actors_use_case`.
- Produces: tools `list_cards` → `{"cards": [{id, name, due_day, is_active}]}` e `list_actors` → `{"actors": [{id, name}]}`.

- [ ] **Step 1: Escrever o teste que falha**

Crie `backend/modules/ai/mcp/tests/test_directory_tools.py`:

```python
from unittest.mock import Mock

from django.test import SimpleTestCase

from modules.ai.mcp.tools.directory import call_list_actors, call_list_cards


class TestListCardsTool(SimpleTestCase):
    def test_maps_card_fields(self):
        use_case = Mock()
        use_case.execute.return_value = [
            {"id": 1, "name": "Nubank", "due_day": 10, "is_active": True, "extra": "x"}
        ]

        result = call_list_cards(arguments={}, use_case=use_case, user_id=7)

        use_case.execute.assert_called_once_with(7)
        self.assertEqual(
            result["cards"], [{"id": 1, "name": "Nubank", "due_day": 10, "is_active": True}]
        )


class TestListActorsTool(SimpleTestCase):
    def test_maps_actor_fields(self):
        use_case = Mock()
        use_case.execute.return_value = [{"id": 3, "name": "Giovanna", "total_spent": "999.00"}]

        result = call_list_actors(arguments={}, use_case=use_case, user_id=7)

        use_case.execute.assert_called_once_with(7, without_sub_transactions=True)
        self.assertEqual(result["actors"], [{"id": 3, "name": "Giovanna"}])
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/test_directory_tools.py -q
```

Esperado: FAIL com `ModuleNotFoundError`.

- [ ] **Step 3: Implementar container + tools**

Em `backend/modules/ai/mcp/container.py`, importe `from modules.cards.container import CardsContainer` e adicione:

```python
    cards_container = providers.Singleton(CardsContainer)
```

Crie `backend/modules/ai/mcp/tools/directory.py`:

```python
LIST_CARDS_DESCRIPTION = (
    "Lista os cartões do usuário com id, nome, dia de vencimento e se está ativo. "
    "Use para resolver card_id antes de filtrar por cartão."
)

LIST_ACTORS_DESCRIPTION = (
    "Lista os atores (pessoas/entidades) do usuário com id e nome. "
    "Use para resolver actor_id antes de filtrar por ator."
)


def call_list_cards(*, arguments: dict, use_case, user_id: int) -> dict:
    cards = use_case.execute(user_id)
    return {
        "cards": [
            {"id": card["id"], "name": card["name"], "due_day": card["due_day"], "is_active": card["is_active"]}
            for card in cards
        ]
    }


def call_list_actors(*, arguments: dict, use_case, user_id: int) -> dict:
    actors = use_case.execute(user_id, without_sub_transactions=True)
    return {"actors": [{"id": actor["id"], "name": actor["name"]} for actor in actors]}
```

Em `backend/modules/ai/mcp/tools/__init__.py`, importe `from modules.ai.mcp.tools import directory` e adicione em `TOOLS`:

```python
    {
        "name": "list_cards",
        "description": directory.LIST_CARDS_DESCRIPTION,
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_actors",
        "description": directory.LIST_ACTORS_DESCRIPTION,
        "inputSchema": {"type": "object", "properties": {}},
    },
```

e em `HANDLERS`:

```python
    "list_cards": lambda arguments, container, user_id: directory.call_list_cards(
        arguments=arguments,
        use_case=container.cards_container().list_cards_use_case(),
        user_id=user_id,
    ),
    "list_actors": lambda arguments, container, user_id: directory.call_list_actors(
        arguments=arguments,
        use_case=container.transactions_container().list_actors_use_case(),
        user_id=user_id,
    ),
```

- [ ] **Step 4: Rodar as suítes**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/ modules/transactions/tests/ -q
```

Esperado: tudo verde, incluindo o teste de contrato `TOOLS == HANDLERS` (agora 13 tools).

- [ ] **Step 5: Commit**

```bash
git add backend/modules/ai/mcp/container.py backend/modules/ai/mcp/tools/directory.py backend/modules/ai/mcp/tools/__init__.py backend/modules/ai/mcp/tests/test_directory_tools.py
git commit -m "feat: adiciona list_cards e list_actors ao MCP"
```

---

### Task 9: Integração, docs e fechamento

**Files:**
- Modify: `backend/modules/ai/mcp/http/tests/test_mcp_view.py`
- Modify: `docs/MCP_SETUP.md`

**Interfaces:**
- Consumes: tudo das tasks anteriores.

- [ ] **Step 1: Corrigir o setUp quebrado do teste de integração**

O teste atual passa `client_id="mcp_x"` para `MCPAccessToken`, mas o modelo usa FK `client`. Em `setUp`:

```python
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="u@u.com", password="x")
        oauth_client = MCPOAuthClient.objects.create(
            client_id="mcp_x", name="X", redirect_uris=[], user_id=self.user.id,
        )
        gen = TokenGeneratorService()
        plaintext, h = gen.generate_access_token()
        MCPAccessToken.objects.create(
            token_hash=h, client=oauth_client, user_id=self.user.id,
            scope="mcp:read",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        self.token = plaintext
```

- [ ] **Step 2: Atualizar `test_initialize` e `test_tools_list`**

```python
    def test_initialize(self):
        resp = self._post({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}},
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["id"], 1)
        self.assertEqual(body["result"]["serverInfo"]["name"], "poupix-mcp")
        self.assertEqual(body["result"]["serverInfo"]["version"], "0.4.0")
        self.assertIn("fatura", body["result"]["instructions"].lower())
        self.assertIn("prompts", body["result"]["capabilities"])

    def test_tools_list(self):
        resp = self._post({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        names = sorted(t["name"] for t in body["result"]["tools"])
        self.assertEqual(
            names,
            sorted([
                "list_transactions", "get_transaction", "create_transaction",
                "update_transaction", "create_sub_transaction", "update_sub_transaction",
                "list_enums", "get_projection", "set_goals",
                "list_sub_transactions", "summarize_spending", "list_cards", "list_actors",
            ]),
        )

    def test_prompts_list(self):
        resp = self._post({"jsonrpc": "2.0", "id": 3, "method": "prompts/list"})
        self.assertEqual(resp.status_code, 200)
        names = sorted(p["name"] for p in resp.json()["result"]["prompts"])
        self.assertEqual(names, ["onde_cortar_gastos", "resumo_mensal"])
```

- [ ] **Step 3: Rodar a integração**

```bash
cd backend && MCP_PG_INTEGRATION=1 /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/http/tests/test_mcp_view.py -q
```

Esperado: `5 passed`.

- [ ] **Step 4: Reescrever o `docs/MCP_SETUP.md`**

Atualize o documento para refletir a 0.4:

- Tabela de tools com as 13, parâmetros e semântica `due_*` vs `purchase_*`.
- Seção "Instructions": o agente recebe contexto no handshake (fatura canônica, BRL, escopo).
- Seção "Prompts": `resumo_mensal` e `onde_cortar_gastos` (no opencode aparecem como `/poupix:resumo_mensal`).
- Remover a tabela obsoleta de `execute_sql`/`describe_schema`.
- Manter o setup local (role read-only, `POUPIX_MCP_USER_ID`, cliente stdio) — ele segue válido.
- Nota de breaking: `month`/`start`/`end` → `due_month`/`due_start`/`due_end`.

- [ ] **Step 5: Rodar a suíte completa (unit + integração)**

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/ modules/transactions/tests/ -q && MCP_PG_INTEGRATION=1 /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/http/tests/test_mcp_view.py -q
```

Esperado: tudo verde.

- [ ] **Step 6: Commit**

```bash
git add backend/modules/ai/mcp/http/tests/test_mcp_view.py docs/MCP_SETUP.md
git commit -m "docs: atualiza setup do MCP e testes de integração para 0.4.0"
```

---

## Verificação final (após a última task)

```bash
cd backend && /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/tests/ modules/transactions/tests/ -q
cd backend && MCP_PG_INTEGRATION=1 /tmp/opencode/venv/bin/python -m pytest modules/ai/mcp/http/tests/test_mcp_view.py -q
```

E um smoke real contra a produção (após deploy, fora do escopo deste plano): chamar `tools/list` e `summarize_spending` com o token OAuth existente.
