import json
import logging

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from modules.ai.container import AIContainer
from modules.ai.mcp.container import MCPContainer
from modules.ai.mcp.http.auth import user_id_from_bearer_token
from modules.ai.mcp.tools import TOOLS, dispatch_tool


logger = logging.getLogger("modules.ai.mcp")

_ai_container = AIContainer()
_mcp_container = MCPContainer(
    ask_use_case=_ai_container.ask_use_case(),
    ai_call_repository=_ai_container.ai_call_repository(),
)


PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "poupix-mcp", "version": "0.3.0"}


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
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = payload.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        result = dispatch_tool(name, arguments, _mcp_container, user_id)
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
