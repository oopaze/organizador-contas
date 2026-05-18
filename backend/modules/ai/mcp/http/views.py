import json
import logging

from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from modules.ai.mcp.container import MCPContainer
from modules.ai.mcp.http.auth import user_id_from_bearer_token
from modules.ai.mcp.tools.execute_sql import (
    EXECUTE_SQL_DESCRIPTION, call_execute_sql,
)
from modules.ai.mcp.tools.describe_schema import (
    DESCRIBE_SCHEMA_DESCRIPTION, call_describe_schema,
)
from modules.ai.mcp.tools.list_enums import (
    LIST_ENUMS_DESCRIPTION, call_list_enums,
)
from modules.ai.mcp.exceptions import MCPError


logger = logging.getLogger("modules.ai.mcp")

_mcp_container = MCPContainer()


PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "poupix-mcp", "version": "0.2.0"}


def _tools_list() -> list[dict]:
    return [
        {
            "name": "execute_sql",
            "description": EXECUTE_SQL_DESCRIPTION,
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        {
            "name": "describe_schema",
            "description": DESCRIBE_SCHEMA_DESCRIPTION,
            "inputSchema": {
                "type": "object",
                "properties": {"table": {"type": "string"}},
            },
        },
        {
            "name": "list_enums",
            "description": LIST_ENUMS_DESCRIPTION,
            "inputSchema": {"type": "object", "properties": {}},
        },
    ]


def _call_tool(name: str, arguments: dict, user_id: int) -> dict:
    if name == "execute_sql":
        return call_execute_sql(
            query=arguments["query"],
            use_case=_mcp_container.execute_sql_use_case(),
            user_id=user_id,
        )
    if name == "describe_schema":
        return call_describe_schema(
            table=arguments.get("table"),
            use_case=_mcp_container.describe_schema_use_case(),
        )
    if name == "list_enums":
        return call_list_enums(
            use_case=_mcp_container.list_enums_use_case(),
        )
    return {"error": {"code": "UNKNOWN_TOOL", "message": f"unknown tool: {name}"}}


def _dispatch(payload: dict, user_id: int) -> dict | None:
    method = payload.get("method")
    rid = payload.get("id")
    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": rid,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
            },
        }
    if method == "notifications/initialized":
        return None  # notification — no response
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": _tools_list()}}
    if method == "tools/call":
        params = payload.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        result = _call_tool(name, arguments, user_id)
        return {
            "jsonrpc": "2.0", "id": rid,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                "isError": "error" in result,
            },
        }
    if method == "ping":
        return {"jsonrpc": "2.0", "id": rid, "result": {}}
    return {
        "jsonrpc": "2.0", "id": rid,
        "error": {"code": -32601, "message": f"method not found: {method}"},
    }


@csrf_exempt
@require_POST
def mcp_endpoint(request):
    user_id = user_id_from_bearer_token(request.headers.get("Authorization"))
    if user_id is None:
        resp = JsonResponse({"error": "invalid_token"}, status=401)
        resp["WWW-Authenticate"] = 'Bearer realm="mcp", error="invalid_token"'
        return resp

    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("invalid JSON")

    if isinstance(payload, list):
        # Batch — handle each, filter out notifications
        responses = []
        for item in payload:
            r = _dispatch(item, user_id)
            if r is not None:
                responses.append(r)
        if not responses:
            return JsonResponse({}, status=204, safe=False)
        return JsonResponse(responses, safe=False)

    response = _dispatch(payload, user_id)
    if response is None:
        return JsonResponse({}, status=204)
    return JsonResponse(response)
