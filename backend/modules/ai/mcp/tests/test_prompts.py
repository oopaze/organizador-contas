from django.test import SimpleTestCase
from django.utils import timezone

from modules.ai.mcp.http import views
from modules.ai.mcp.prompts import get_prompt, list_prompts


def _previous_month(mes: str) -> str:
    year, month = int(mes[:4]), int(mes[5:7])
    if month == 1:
        return f"{year - 1}-12"
    return f"{year}-{month - 1:02d}"


class TestPromptRegistry(SimpleTestCase):
    def test_lists_two_prompts(self):
        names = [prompt["name"] for prompt in list_prompts()]
        self.assertEqual(names, ["resumo_mensal", "onde_cortar_gastos"])

    def test_resumo_mensal_embeds_month(self):
        payload = get_prompt("resumo_mensal", {"mes": "2026-09"})

        text = payload["messages"][0]["content"]["text"]
        self.assertIn("2026-09", text)
        self.assertIn("summarize_spending", text)

    def test_resumo_mensal_without_month_uses_current_month(self):
        atual = timezone.localdate().strftime("%Y-%m")
        anterior = _previous_month(atual)

        text = get_prompt("resumo_mensal", {})["messages"][0]["content"]["text"]

        self.assertIn(f"due_month={atual}", text)
        self.assertIn(f"due_month={anterior}", text)
        self.assertNotIn("sem due_month", text)

    def test_resumo_mensal_with_explicit_month_embeds_previous(self):
        text = get_prompt("resumo_mensal", {"mes": "2026-01"})["messages"][0]["content"]["text"]

        self.assertIn("due_month=2026-01", text)
        self.assertIn("due_month=2025-12", text)

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
