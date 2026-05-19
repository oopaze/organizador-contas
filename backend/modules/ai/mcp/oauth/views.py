import json
import logging
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from modules.ai.mcp.oauth.container import OAuthContainer
from modules.ai.mcp.oauth.exceptions import OAuthError


logger = logging.getLogger("modules.ai.mcp")

container = OAuthContainer()


def _oauth_error(exc: OAuthError, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": exc.error, "error_description": exc.message}, status=status)


@csrf_exempt
@require_POST
def register_client(request):
    try:
        body = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("invalid JSON")
    redirect_uris = body.get("redirect_uris") or []
    client_name = body.get("client_name") or "Unknown Client"
    try:
        client = container.register_client_use_case().execute(
            name=client_name, redirect_uris=redirect_uris,
        )
    except OAuthError as exc:
        return _oauth_error(exc)
    return JsonResponse({
        "client_id": client.client_id,
        "client_name": client.name,
        "redirect_uris": client.redirect_uris,
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
    }, status=201)


@require_GET
def authorize(request):
    """
    Entry point for OAuth authorization from MCP clients (Claude, ChatGPT).
    Hands off to the SPA's /oauth/authorize route, preserving the query string.
    The SPA renders the consent UI and POSTs to /api/v1/mcp/oauth/authorize/.
    """
    qs = request.META.get("QUERY_STRING", "")
    target = f"{settings.MCP_OAUTH_FRONTEND_URL.rstrip('/')}/oauth/authorize"
    if qs:
        target = f"{target}?{qs}"
    return HttpResponseRedirect(target)


@csrf_exempt
@require_POST
def token(request):
    p = request.POST
    if p.get("grant_type") != "authorization_code":
        return JsonResponse({"error": "unsupported_grant_type"}, status=400)
    code = p.get("code")
    client_id = p.get("client_id")
    redirect_uri = p.get("redirect_uri")
    code_verifier = p.get("code_verifier")
    if not all([code, client_id, redirect_uri, code_verifier]):
        return JsonResponse({"error": "invalid_request"}, status=400)
    try:
        result = container.exchange_code_use_case().execute(
            code=code, client_id=client_id, redirect_uri=redirect_uri,
            code_verifier=code_verifier,
        )
    except OAuthError as exc:
        return _oauth_error(exc)
    return JsonResponse(result)


@csrf_exempt
@require_POST
def revoke(request):
    plaintext = request.POST.get("token")
    if not plaintext:
        return JsonResponse({"error": "invalid_request"}, status=400)
    container.revoke_use_case().execute_by_token(plaintext_token=plaintext)
    return JsonResponse({})


@require_GET
def well_known_authorization_server(request):
    issuer = settings.MCP_OAUTH_ISSUER
    return JsonResponse({
        "issuer": issuer,
        "authorization_endpoint": f"{issuer}/oauth/authorize",
        "token_endpoint": f"{issuer}/oauth/token",
        "registration_endpoint": f"{issuer}/oauth/register",
        "revocation_endpoint": f"{issuer}/oauth/revoke",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["none"],
        "scopes_supported": ["mcp:read"],
    })


@require_GET
def well_known_protected_resource(request):
    issuer = settings.MCP_OAUTH_ISSUER
    return JsonResponse({
        "resource": f"{issuer}/mcp",
        "authorization_servers": [issuer],
        "scopes_supported": ["mcp:read"],
        "bearer_methods_supported": ["header"],
    })


@require_GET
def mcp_client_info(request, client_id: str):
    """Public endpoint: the SPA consent screen calls this to render the client name."""
    client = container.client_repository().get_by_client_id(client_id)
    if client is None:
        return JsonResponse({"error": "not_found"}, status=404)
    return JsonResponse({
        "client_id": client.client_id,
        "name": client.name,
        "redirect_uris": client.redirect_uris,
    })


def _authenticate_jwt(request):
    """Returns the authenticated user, or None. Mirrors JWTAuthentication's logic."""
    from modules.userdata.authentication import JWTAuthentication
    auth = JWTAuthentication()
    try:
        result = auth.authenticate(request)
    except Exception:
        return None
    if result is None:
        return None
    user, _token = result
    return user


@csrf_exempt
@require_POST
def authorize_api(request):
    """
    Called by the SPA consent screen when the user clicks "Autorizar".
    Issues an auth code and returns the redirect URL for the client.
    """
    user = _authenticate_jwt(request)
    if user is None:
        return JsonResponse({"error": "unauthorized"}, status=401)
    try:
        body = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid_request", "error_description": "invalid JSON"}, status=400)

    client_id = body.get("client_id")
    redirect_uri = body.get("redirect_uri")
    code_challenge = body.get("code_challenge")
    code_challenge_method = body.get("code_challenge_method", "S256")
    scope = body.get("scope", "mcp:read")
    state = body.get("state", "")

    if not all([client_id, redirect_uri, code_challenge]):
        return JsonResponse(
            {"error": "invalid_request", "error_description": "missing required parameters"},
            status=400,
        )

    try:
        auth_code = container.authorize_use_case().execute(
            client_id=client_id, user_id=user.id,
            redirect_uri=redirect_uri, code_challenge=code_challenge,
            code_challenge_method=code_challenge_method, scope=scope,
        )
    except OAuthError as exc:
        return _oauth_error(exc)

    qs = urlencode({"code": auth_code.code, "state": state})
    return JsonResponse({"redirect_to": f"{redirect_uri}?{qs}"})


@login_required
@require_http_methods(["GET"])
def list_connections(request):
    items = container.list_connections_use_case().execute(user_id=request.user.id)
    return JsonResponse({"connections": items})


@login_required
@require_http_methods(["POST"])
def revoke_connection(request, client_id: str):
    n = container.revoke_use_case().execute_by_client(
        client_id=client_id, user_id=request.user.id,
    )
    return JsonResponse({"revoked": n})
