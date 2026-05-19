# MCP OAuth Consent on Frontend — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Django-rendered OAuth consent page with a React route, and migrate the MCP connection endpoints from Django-session auth to JWT.

**Architecture:** When Claude/ChatGPT hits `GET /oauth/authorize?...`, the backend now 302s to the SPA route `/oauth/authorize?...`. The React page renders a consent UI using the existing design system, calls a new JWT-auth'd `POST /api/v1/mcp/oauth/authorize/` to mint an auth code, then browser-navigates to the OAuth `redirect_uri`. The connection list/revoke endpoints move to JWT auth so the integrations page works in prod.

**Tech Stack:** Django 6 (function views, `JsonResponse`), pytest + `MCP_PG_INTEGRATION=1` for integration tests, React 18 + React Router 6 + Vite, Tailwind + Radix UI components, `apiRequest` helper for HTTP.

**Spec:** [docs/superpowers/specs/2026-05-19-mcp-oauth-consent-on-frontend-design.md](../specs/2026-05-19-mcp-oauth-consent-on-frontend-design.md)

---

## File Map

**Backend — modify:**
- `backend/infra/secrets.py` — add `MCP_OAUTH_FRONTEND_URL` env var read.
- `backend/modules/ai/mcp/oauth/urls.py` — register new endpoints, drop POST handler on `/oauth/authorize` (the GET becomes a redirect; POST goes away).
- `backend/modules/ai/mcp/oauth/views.py` — rewrite `authorize` as 302 to SPA; add `mcp_client_info`, `authorize_api`; switch `list_connections` and `revoke_connection` to JWT auth.
- `backend/modules/ai/mcp/oauth/tests/test_views.py` — replace the form-post OAuth tests with the new JSON-endpoint flow; cover the 302 from the old endpoint.

**Backend — delete:**
- `backend/modules/ai/mcp/oauth/templates/mcp_oauth/consent.html` — no longer used.
- `backend/modules/ai/mcp/oauth/templates/` — empty after the file delete; remove the directory.

**Frontend — create:**
- `frontend/src/services/mcp/oauthAuthorize.ts` — two API calls: `fetchMCPClient`, `approveMCPAuthorization`.
- `frontend/src/app/pages/oauth-authorize-page.tsx` — the consent screen.

**Frontend — modify:**
- `frontend/src/app/pages/routes.tsx` — mount the new page at `/oauth/authorize` outside the Layout/ProtectedRoute wrapper.
- `frontend/src/app/components/login-page.tsx` — honor `?next=` after login.

---

## Tasks

### Task 1: Add `MCP_OAUTH_FRONTEND_URL` setting

**Files:**
- Modify: `backend/infra/secrets.py`

- [ ] **Step 1: Read the current file**

```bash
cat backend/infra/secrets.py | grep -n MCP_OAUTH
```
Expected: a single line `MCP_OAUTH_ISSUER = environ.get("MCP_OAUTH_ISSUER", "http://localhost:8000")`.

- [ ] **Step 2: Add the new env-driven setting right after `MCP_OAUTH_ISSUER`**

```python
MCP_OAUTH_FRONTEND_URL = environ.get("MCP_OAUTH_FRONTEND_URL", "http://localhost:5173")
```

- [ ] **Step 3: Commit**

```bash
git add backend/infra/secrets.py
git commit -m "feat(mcp): add MCP_OAUTH_FRONTEND_URL setting"
```

---

### Task 2: Test — `GET /oauth/authorize` 302s to the SPA

**Files:**
- Test: `backend/modules/ai/mcp/oauth/tests/test_views.py`

This test reflects the new contract: the backend hands the consent UI off to the SPA. It will fail today (current code renders the Django template).

- [ ] **Step 1: Add the new test class at the bottom of the file**

```python
class TestAuthorizeRedirect(TestCase):
    def setUp(self):
        self.client = Client()
        from modules.ai.mcp.models import MCPOAuthClient
        MCPOAuthClient.objects.create(
            client_id="mcp_abc", name="Claude",
            redirect_uris=["https://app.example.com/cb"],
        )

    def test_get_redirects_to_spa_with_query_string(self):
        from django.test import override_settings
        with override_settings(MCP_OAUTH_FRONTEND_URL="https://app.poupix.test"):
            resp = self.client.get(
                "/oauth/authorize",
                {
                    "client_id": "mcp_abc",
                    "redirect_uri": "https://app.example.com/cb",
                    "code_challenge": "abc",
                    "code_challenge_method": "S256",
                    "scope": "mcp:read",
                    "state": "xyz",
                },
            )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            resp.url.startswith("https://app.poupix.test/oauth/authorize?"),
            resp.url,
        )
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(resp.url).query)
        self.assertEqual(qs["client_id"], ["mcp_abc"])
        self.assertEqual(qs["state"], ["xyz"])
        self.assertEqual(qs["code_challenge"], ["abc"])
```

- [ ] **Step 2: Run the new test and confirm it fails**

```bash
cd backend && MCP_PG_INTEGRATION=1 pytest modules/ai/mcp/oauth/tests/test_views.py::TestAuthorizeRedirect -v
```
Expected: FAIL — currently the view renders `consent.html` and returns 200, not a 302 to the SPA.

- [ ] **Step 3: Commit the failing test**

```bash
git add backend/modules/ai/mcp/oauth/tests/test_views.py
git commit -m "test(mcp): authorize GET should 302 to SPA consent route"
```

---

### Task 3: Implement the `GET /oauth/authorize` → SPA redirect

**Files:**
- Modify: `backend/modules/ai/mcp/oauth/views.py`

- [ ] **Step 1: Replace the `authorize` view**

Open `backend/modules/ai/mcp/oauth/views.py`. Replace the entire existing `authorize` function (the `@login_required(...) def authorize(request): ...` block, ending at the `return HttpResponseRedirect(...)` before the `@csrf_exempt @require_POST def token` block) with:

```python
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
```

Then remove the now-unused `from django.shortcuts import render` import at the top. Leave `from django.contrib.auth.decorators import login_required` for now — `list_connections` and `revoke_connection` still use it; Task 9 removes it. Leave `from urllib.parse import urlencode` — Task 7 needs it again.

- [ ] **Step 2: Run the test and confirm it passes**

```bash
cd backend && MCP_PG_INTEGRATION=1 pytest modules/ai/mcp/oauth/tests/test_views.py::TestAuthorizeRedirect -v
```
Expected: PASS.

- [ ] **Step 3: Run the full OAuth view test module to check what's broken**

```bash
cd backend && MCP_PG_INTEGRATION=1 pytest modules/ai/mcp/oauth/tests/test_views.py -v
```
Expected: `TestOAuthFlow.test_full_flow` and `TestOAuthFlow.test_pkce_failure` now fail (they POST to `/oauth/authorize` with `decision=allow`, which no longer accepts POST). That's intentional and Task 5 replaces them.

- [ ] **Step 4: Commit**

```bash
git add backend/modules/ai/mcp/oauth/views.py
git commit -m "feat(mcp): redirect oauth authorize GET to SPA consent route"
```

---

### Task 4: Test — `GET /api/v1/mcp/oauth/client/<id>/`

**Files:**
- Test: `backend/modules/ai/mcp/oauth/tests/test_views.py`

- [ ] **Step 1: Add a test class at the bottom of the file**

```python
class TestClientInfoEndpoint(TestCase):
    def setUp(self):
        self.client = Client()
        from modules.ai.mcp.models import MCPOAuthClient
        MCPOAuthClient.objects.create(
            client_id="mcp_known",
            name="Claude",
            redirect_uris=["https://claude.ai/cb"],
        )

    def test_returns_client_info_without_auth(self):
        resp = self.client.get("/api/v1/mcp/oauth/client/mcp_known/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["client_id"], "mcp_known")
        self.assertEqual(body["name"], "Claude")
        self.assertEqual(body["redirect_uris"], ["https://claude.ai/cb"])

    def test_unknown_client_returns_404(self):
        resp = self.client.get("/api/v1/mcp/oauth/client/missing/")
        self.assertEqual(resp.status_code, 404)
```

- [ ] **Step 2: Run and confirm it fails**

```bash
cd backend && MCP_PG_INTEGRATION=1 pytest modules/ai/mcp/oauth/tests/test_views.py::TestClientInfoEndpoint -v
```
Expected: FAIL with 404 on `/api/v1/mcp/oauth/client/...` (URL not registered yet).

- [ ] **Step 3: Commit**

```bash
git add backend/modules/ai/mcp/oauth/tests/test_views.py
git commit -m "test(mcp): client-info endpoint contract"
```

---

### Task 5: Implement `GET /api/v1/mcp/oauth/client/<id>/`

**Files:**
- Modify: `backend/modules/ai/mcp/oauth/views.py`
- Modify: `backend/modules/ai/mcp/oauth/urls.py`

- [ ] **Step 1: Add the view**

In `backend/modules/ai/mcp/oauth/views.py`, add this after `well_known_protected_resource`:

```python
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
```

- [ ] **Step 2: Register the URL**

Open `backend/modules/ai/mcp/oauth/urls.py`. Add this line inside `urlpatterns`, before the existing `api/v1/mcp/connections/` lines:

```python
    path("api/v1/mcp/oauth/client/<str:client_id>/", views.mcp_client_info, name="mcp_oauth_client_info"),
```

- [ ] **Step 3: Run the tests**

```bash
cd backend && MCP_PG_INTEGRATION=1 pytest modules/ai/mcp/oauth/tests/test_views.py::TestClientInfoEndpoint -v
```
Expected: both tests pass.

- [ ] **Step 4: Commit**

```bash
git add backend/modules/ai/mcp/oauth/views.py backend/modules/ai/mcp/oauth/urls.py
git commit -m "feat(mcp): add public client-info endpoint"
```

---

### Task 6: Test — `POST /api/v1/mcp/oauth/authorize/`

**Files:**
- Test: `backend/modules/ai/mcp/oauth/tests/test_views.py`

- [ ] **Step 1: Add a test class**

```python
class TestAuthorizeApiEndpoint(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="u@u.com", password="x", is_active=True)
        self.redirect_uri = "https://app.example.com/cb"
        self.verifier, self.challenge = pkce_pair()
        from modules.ai.mcp.models import MCPOAuthClient
        MCPOAuthClient.objects.create(
            client_id="mcp_x", name="Claude",
            redirect_uris=[self.redirect_uri],
        )

    def _jwt_for(self, user):
        from django.conf import settings as dj_settings
        from modules.userdata.gateways.jwt import JWTGateway
        return JWTGateway(secret_key=dj_settings.SECRET_KEY).create_access_token(user_id=user.id)

    def test_happy_path_returns_redirect_to_with_code_and_state(self):
        token = self._jwt_for(self.user)
        resp = self.client.post(
            "/api/v1/mcp/oauth/authorize/",
            data=json.dumps({
                "client_id": "mcp_x",
                "redirect_uri": self.redirect_uri,
                "code_challenge": self.challenge,
                "code_challenge_method": "S256",
                "scope": "mcp:read",
                "state": "st-1",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        body = resp.json()
        self.assertIn("redirect_to", body)
        self.assertTrue(body["redirect_to"].startswith(self.redirect_uri + "?"))
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(body["redirect_to"]).query)
        self.assertIn("code", qs)
        self.assertEqual(qs["state"], ["st-1"])

    def test_requires_jwt(self):
        resp = self.client.post(
            "/api/v1/mcp/oauth/authorize/",
            data=json.dumps({"client_id": "mcp_x"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_mismatched_redirect_uri_returns_400(self):
        token = self._jwt_for(self.user)
        resp = self.client.post(
            "/api/v1/mcp/oauth/authorize/",
            data=json.dumps({
                "client_id": "mcp_x",
                "redirect_uri": "https://evil.example.com/cb",
                "code_challenge": self.challenge,
                "code_challenge_method": "S256",
                "scope": "mcp:read",
                "state": "st",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["error"], "invalid_request")
```

You also need the JWT helper. Confirm it exists with the right method name:

```bash
grep -n 'create_access_token\|def create_' backend/modules/userdata/gateways/jwt.py
```
If the method name is different (e.g. `issue_access_token`, `generate_token`), update the `_jwt_for` helper above to match. Read the file to confirm: `cat backend/modules/userdata/gateways/jwt.py`.

- [ ] **Step 2: Run and confirm it fails**

```bash
cd backend && MCP_PG_INTEGRATION=1 pytest modules/ai/mcp/oauth/tests/test_views.py::TestAuthorizeApiEndpoint -v
```
Expected: all three tests fail with 404 (endpoint not registered yet).

- [ ] **Step 3: Commit**

```bash
git add backend/modules/ai/mcp/oauth/tests/test_views.py
git commit -m "test(mcp): authorize API endpoint contract"
```

---

### Task 7: Implement `POST /api/v1/mcp/oauth/authorize/`

**Files:**
- Modify: `backend/modules/ai/mcp/oauth/views.py`
- Modify: `backend/modules/ai/mcp/oauth/urls.py`

- [ ] **Step 1: Add the view**

In `backend/modules/ai/mcp/oauth/views.py`, add this near the other view functions (e.g. just below `mcp_client_info`):

```python
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
```

`urlencode` is already imported at the top of the file (Task 3 left it in place).

- [ ] **Step 2: Register the URL**

In `backend/modules/ai/mcp/oauth/urls.py`, add this line inside `urlpatterns`, right after the client-info path from Task 5:

```python
    path("api/v1/mcp/oauth/authorize/", views.authorize_api, name="mcp_oauth_authorize_api"),
```

- [ ] **Step 3: Run the tests**

```bash
cd backend && MCP_PG_INTEGRATION=1 pytest modules/ai/mcp/oauth/tests/test_views.py::TestAuthorizeApiEndpoint -v
```
Expected: all three tests pass.

- [ ] **Step 4: Commit**

```bash
git add backend/modules/ai/mcp/oauth/views.py backend/modules/ai/mcp/oauth/urls.py
git commit -m "feat(mcp): add JSON authorize endpoint for SPA consent"
```

---

### Task 8: Replace the legacy `test_full_flow` with the new flow

**Files:**
- Modify: `backend/modules/ai/mcp/oauth/tests/test_views.py`

`TestOAuthFlow.test_full_flow` and `TestOAuthFlow.test_pkce_failure` still POST to `/oauth/authorize` with `decision=allow`. That handler no longer exists. Rewrite them to use the JSON endpoint.

- [ ] **Step 1: Replace `test_full_flow`**

Find the existing `test_full_flow` method (around line 52). Replace its body with:

```python
    def test_full_flow(self):
        client_id = self._register()
        from modules.userdata.gateways.jwt import JWTGateway
        from django.conf import settings as dj_settings
        token = JWTGateway(secret_key=dj_settings.SECRET_KEY).create_access_token(user_id=self.user.id)
        resp = self.client.post(
            "/api/v1/mcp/oauth/authorize/",
            data=json.dumps({
                "client_id": client_id,
                "redirect_uri": self.redirect_uri,
                "code_challenge": self.challenge,
                "code_challenge_method": "S256",
                "scope": "mcp:read",
                "state": "xyz",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(resp.json()["redirect_to"]).query)
        code = qs["code"][0]
        # Token exchange — unchanged
        resp = self.client.post("/oauth/token", {
            "grant_type": "authorization_code",
            "code": code, "client_id": client_id,
            "redirect_uri": self.redirect_uri,
            "code_verifier": self.verifier,
        })
        self.assertEqual(resp.status_code, 200, resp.content)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "Bearer")
```

- [ ] **Step 2: Replace `test_pkce_failure`**

Replace its body with:

```python
    def test_pkce_failure(self):
        client_id = self._register()
        from modules.userdata.gateways.jwt import JWTGateway
        from django.conf import settings as dj_settings
        token = JWTGateway(secret_key=dj_settings.SECRET_KEY).create_access_token(user_id=self.user.id)
        resp = self.client.post(
            "/api/v1/mcp/oauth/authorize/",
            data=json.dumps({
                "client_id": client_id,
                "redirect_uri": self.redirect_uri,
                "code_challenge": self.challenge,
                "code_challenge_method": "S256",
                "scope": "mcp:read",
                "state": "xyz",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        from urllib.parse import urlparse, parse_qs
        code = parse_qs(urlparse(resp.json()["redirect_to"]).query)["code"][0]
        resp = self.client.post("/oauth/token", {
            "grant_type": "authorization_code",
            "code": code, "client_id": client_id,
            "redirect_uri": self.redirect_uri,
            "code_verifier": "WRONG",
        })
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["error"], "invalid_grant")
```

The `self.client.force_login(self.user)` line in both methods can be removed — JWT is now the auth path.

- [ ] **Step 3: Run the full module**

```bash
cd backend && MCP_PG_INTEGRATION=1 pytest modules/ai/mcp/oauth/tests/test_views.py -v
```
Expected: all tests pass except possibly `TestConnectionsAPI` (covered in Task 9).

- [ ] **Step 4: Commit**

```bash
git add backend/modules/ai/mcp/oauth/tests/test_views.py
git commit -m "test(mcp): port OAuth flow tests to JSON authorize endpoint"
```

---

### Task 9: Migrate connection endpoints to JWT

**Files:**
- Modify: `backend/modules/ai/mcp/oauth/views.py`
- Modify: `backend/modules/ai/mcp/oauth/tests/test_views.py`

The existing `list_connections` and `revoke_connection` are decorated with `@login_required` (session-based). They need to validate JWT instead so the React integrations page works.

- [ ] **Step 1: Update `TestConnectionsAPI` to use JWT**

In `backend/modules/ai/mcp/oauth/tests/test_views.py`, find `class TestConnectionsAPI` and replace it with:

```python
class TestConnectionsAPI(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="u@u.com", password="x")
        from modules.ai.mcp.models import MCPOAuthClient
        MCPOAuthClient.objects.create(client_id="mcp_a", name="A", redirect_uris=[], user_id=self.user.id)
        MCPOAuthClient.objects.create(client_id="mcp_b", name="B", redirect_uris=[], user_id=self.user.id)
        from modules.userdata.gateways.jwt import JWTGateway
        from django.conf import settings as dj_settings
        self.token = JWTGateway(secret_key=dj_settings.SECRET_KEY).create_access_token(user_id=self.user.id)
        self.auth = f"Bearer {self.token}"

    def test_list_connections(self):
        resp = self.client.get("/api/v1/mcp/connections/", HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(resp.status_code, 200)
        names = [c["name"] for c in resp.json()["connections"]]
        self.assertIn("A", names)
        self.assertIn("B", names)

    def test_revoke_connection(self):
        resp = self.client.post(
            "/api/v1/mcp/connections/mcp_a/revoke/",
            HTTP_AUTHORIZATION=self.auth,
        )
        self.assertEqual(resp.status_code, 200)

    def test_list_requires_jwt(self):
        resp = self.client.get("/api/v1/mcp/connections/")
        self.assertEqual(resp.status_code, 401)
```

- [ ] **Step 2: Run and confirm the new test fails**

```bash
cd backend && MCP_PG_INTEGRATION=1 pytest modules/ai/mcp/oauth/tests/test_views.py::TestConnectionsAPI -v
```
Expected: `test_list_requires_jwt` fails — current code uses `@login_required(login_url="/")` so it returns 302, not 401. The other two also fail because they no longer `force_login`.

- [ ] **Step 3: Rewrite the connection views**

In `backend/modules/ai/mcp/oauth/views.py`, find `list_connections` and `revoke_connection` at the bottom of the file. Replace both with:

```python
@csrf_exempt
@require_GET
def list_connections(request):
    user = _authenticate_jwt(request)
    if user is None:
        return JsonResponse({"error": "unauthorized"}, status=401)
    items = container.list_connections_use_case().execute(user_id=user.id)
    return JsonResponse({"connections": items})


@csrf_exempt
@require_POST
def revoke_connection(request, client_id: str):
    user = _authenticate_jwt(request)
    if user is None:
        return JsonResponse({"error": "unauthorized"}, status=401)
    n = container.revoke_use_case().execute_by_client(
        client_id=client_id, user_id=user.id,
    )
    return JsonResponse({"revoked": n})
```

Now `login_required` is unused. Remove the import: delete the line `from django.contrib.auth.decorators import login_required` at the top of the file. Verify: `grep -n login_required backend/modules/ai/mcp/oauth/views.py` should return nothing.

- [ ] **Step 4: Run and confirm tests pass**

```bash
cd backend && MCP_PG_INTEGRATION=1 pytest modules/ai/mcp/oauth/tests/test_views.py::TestConnectionsAPI -v
```
Expected: all three pass.

- [ ] **Step 5: Run the full oauth test directory as a regression check**

```bash
cd backend && MCP_PG_INTEGRATION=1 pytest modules/ai/mcp/oauth/tests/ -v
```
Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add backend/modules/ai/mcp/oauth/views.py backend/modules/ai/mcp/oauth/tests/test_views.py
git commit -m "feat(mcp): migrate connections endpoints to JWT auth"
```

---

### Task 10: Delete the Django consent template

**Files:**
- Delete: `backend/modules/ai/mcp/oauth/templates/mcp_oauth/consent.html`
- Delete: `backend/modules/ai/mcp/oauth/templates/mcp_oauth/` (now empty)
- Delete: `backend/modules/ai/mcp/oauth/templates/` (now empty)

- [ ] **Step 1: Confirm no other code references the template**

```bash
grep -rn 'consent.html\|mcp_oauth/consent' backend/
```
Expected: no matches (Task 3 removed the `render(...)` call).

- [ ] **Step 2: Delete the file and empty parent dirs**

```bash
rm backend/modules/ai/mcp/oauth/templates/mcp_oauth/consent.html
rmdir backend/modules/ai/mcp/oauth/templates/mcp_oauth
rmdir backend/modules/ai/mcp/oauth/templates
```

- [ ] **Step 3: Verify oauth tests still pass**

```bash
cd backend && MCP_PG_INTEGRATION=1 pytest modules/ai/mcp/oauth/tests/ -v
```
Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add -A backend/modules/ai/mcp/oauth/
git commit -m "chore(mcp): remove unused Django consent template"
```

---

### Task 11: Frontend service — `oauthAuthorize.ts`

**Files:**
- Create: `frontend/src/services/mcp/oauthAuthorize.ts`

- [ ] **Step 1: Create the file**

```ts
import { apiRequest } from '../client';

export interface MCPClientInfo {
  client_id: string;
  name: string;
  redirect_uris: string[];
}

export interface AuthorizeParams {
  client_id: string;
  redirect_uri: string;
  code_challenge: string;
  code_challenge_method: string;
  scope: string;
  state: string;
}

export interface AuthorizeResponse {
  redirect_to: string;
}

export async function fetchMCPClient(clientId: string): Promise<MCPClientInfo> {
  return apiRequest<MCPClientInfo>(`/api/v1/mcp/oauth/client/${encodeURIComponent(clientId)}/`);
}

export async function approveMCPAuthorization(
  params: AuthorizeParams,
): Promise<AuthorizeResponse> {
  return apiRequest<AuthorizeResponse>('/api/v1/mcp/oauth/authorize/', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}
```

- [ ] **Step 2: Verify it compiles**

```bash
cd frontend && yarn tsc --noEmit
```
Expected: no errors related to this file. (Pre-existing errors in other files are fine.)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/services/mcp/oauthAuthorize.ts
git commit -m "feat(mcp): add frontend oauth-authorize service"
```

---

### Task 12: Frontend page — `oauth-authorize-page.tsx`

**Files:**
- Create: `frontend/src/app/pages/oauth-authorize-page.tsx`

- [ ] **Step 1: Create the file**

```tsx
import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Skeleton } from '@/app/components/ui/skeleton';
import { Wallet } from 'lucide-react';
import { useAuth } from '@/contexts/auth-context';
import {
  fetchMCPClient,
  approveMCPAuthorization,
  MCPClientInfo,
} from '@/services/mcp/oauthAuthorize';

const REQUIRED_PARAMS = ['client_id', 'redirect_uri', 'code_challenge'] as const;

export const OAuthAuthorizePage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, loading: authLoading } = useAuth();

  const [client, setClient] = useState<MCPClientInfo | null>(null);
  const [loadingClient, setLoadingClient] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [approving, setApproving] = useState(false);

  const clientId = searchParams.get('client_id');
  const redirectUri = searchParams.get('redirect_uri');
  const state = searchParams.get('state') ?? '';
  const codeChallenge = searchParams.get('code_challenge');
  const codeChallengeMethod = searchParams.get('code_challenge_method') ?? 'S256';
  const scope = searchParams.get('scope') ?? 'mcp:read';

  const missingParam = REQUIRED_PARAMS.find(k => !searchParams.get(k));

  // Auth gate — preserve full querystring through login.
  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      const next = encodeURIComponent(location.pathname + location.search);
      navigate(`/login?next=${next}`, { replace: true });
    }
  }, [authLoading, isAuthenticated, navigate, location]);

  // Fetch client info once we know required params exist and user is authed.
  useEffect(() => {
    if (missingParam || !isAuthenticated || !clientId) return;
    setLoadingClient(true);
    fetchMCPClient(clientId)
      .then(setClient)
      .catch(() => setError('Aplicativo não reconhecido.'))
      .finally(() => setLoadingClient(false));
  }, [clientId, isAuthenticated, missingParam]);

  const redirectMatches =
    client && redirectUri && client.redirect_uris.includes(redirectUri);

  async function handleApprove() {
    if (!clientId || !redirectUri || !codeChallenge) return;
    setApproving(true);
    setError(null);
    try {
      const { redirect_to } = await approveMCPAuthorization({
        client_id: clientId,
        redirect_uri: redirectUri,
        code_challenge: codeChallenge,
        code_challenge_method: codeChallengeMethod,
        scope,
        state,
      });
      window.location.assign(redirect_to);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Falha ao autorizar');
      setApproving(false);
    }
  }

  function handleDeny() {
    if (!redirectUri) return;
    const sep = redirectUri.includes('?') ? '&' : '?';
    const qs = new URLSearchParams({ error: 'access_denied', state }).toString();
    window.location.assign(`${redirectUri}${sep}${qs}`);
  }

  if (authLoading || !isAuthenticated) {
    return <Shell><Skeleton className="h-32 w-full" /></Shell>;
  }

  if (missingParam) {
    return (
      <Shell>
        <ErrorCard
          title="Solicitação de autorização inválida"
          message={`Parâmetro ausente: ${missingParam}.`}
        />
      </Shell>
    );
  }

  if (loadingClient) {
    return <Shell><Skeleton className="h-48 w-full" /></Shell>;
  }

  if (!client) {
    return <Shell><ErrorCard title="Aplicativo não reconhecido" message={error ?? ''} /></Shell>;
  }

  return (
    <Shell>
      <Card>
        <CardHeader>
          <CardTitle>Autorizar {client.name}</CardTitle>
          <CardDescription>
            Este aplicativo poderá ler suas finanças no Poupix em modo somente leitura.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded-lg border bg-muted/40 p-4 text-sm">
            <div className="font-medium">Permissão solicitada</div>
            <div className="text-muted-foreground">
              Leitura das suas transações, categorias e atores ({scope}).
            </div>
          </div>

          {!redirectMatches && (
            <div className="rounded-md border border-destructive/40 bg-destructive/5 p-3 text-sm text-destructive">
              URL de retorno não permitida para este aplicativo.
            </div>
          )}

          {error && (
            <div className="rounded-md border border-destructive/40 bg-destructive/5 p-3 text-sm text-destructive">
              {error}
            </div>
          )}

          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={handleDeny} disabled={approving}>
              Negar
            </Button>
            <Button
              onClick={handleApprove}
              disabled={!redirectMatches || approving}
            >
              {approving ? 'Autorizando…' : 'Autorizar'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </Shell>
  );
};

const Shell: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-50 to-teal-100 p-4">
    <div className="w-full max-w-md">
      <div className="text-center mb-6">
        <div className="inline-flex items-center justify-center w-14 h-14 bg-emerald-600 rounded-full mb-3">
          <Wallet className="w-7 h-7 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900">Poupix</h1>
      </div>
      {children}
    </div>
  </div>
);

const ErrorCard: React.FC<{ title: string; message: string }> = ({ title, message }) => (
  <Card>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
      {message && <CardDescription>{message}</CardDescription>}
    </CardHeader>
    <CardContent>
      <a href="/" className="text-sm text-emerald-700 underline">Voltar ao Poupix</a>
    </CardContent>
  </Card>
);
```

- [ ] **Step 2: Verify it compiles**

```bash
cd frontend && yarn tsc --noEmit
```
Expected: no new errors from this file.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/pages/oauth-authorize-page.tsx
git commit -m "feat(mcp): add SPA oauth-authorize consent page"
```

---

### Task 13: Mount the new route

**Files:**
- Modify: `frontend/src/app/pages/routes.tsx`

The page lives outside `<Layout>` and `<ProtectedRoute>` — it manages its own auth gate to preserve the OAuth query string through login.

- [ ] **Step 1: Update the routes**

Open `frontend/src/app/pages/routes.tsx`. After the `import { PublicActorPage } ...` line, add:

```tsx
import { OAuthAuthorizePage } from './oauth-authorize-page';
```

Then, inside the `<Routes>` block, immediately after the `<Route path="/share/actor" ... />` line and before the `<Route element={<ProtectedRoute>...` block, add:

```tsx
{/* OAuth consent — handles its own auth gate */}
<Route path="/oauth/authorize" element={<OAuthAuthorizePage />} />
```

- [ ] **Step 2: Verify it compiles**

```bash
cd frontend && yarn tsc --noEmit
```
Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/pages/routes.tsx
git commit -m "feat(mcp): mount oauth-authorize page at /oauth/authorize"
```

---

### Task 14: Make login honor `?next=`

**Files:**
- Modify: `frontend/src/app/components/login-page.tsx`

After a successful login, redirect to `next` if it's a safe relative path; otherwise fall back to `/`. The existing flow returns to `/` because `AuthProvider.login` sets the user and `<PublicRoute>` (wrapping `LoginPage`) presumably bounces authed users elsewhere — verify by reading `frontend/src/app/components/public-route.tsx` once before writing the code.

- [ ] **Step 1: Read `public-route.tsx`**

```bash
cat frontend/src/app/components/public-route.tsx
```

If `PublicRoute` always redirects to `/`, you'll need to make the redirect target dynamic. Two clean options — pick one:

**(a) Move the post-login redirect into `LoginPage`:** after `await login(...)`, call `navigate(safeNext, { replace: true })` and ensure `PublicRoute` lets authenticated users render `LoginPage` once before the navigate fires. Simpler: have `LoginPage` perform the navigate immediately on success regardless of what `PublicRoute` does.

**(b) Make `PublicRoute` read `?next=`:** less ideal because it leaks the OAuth concept into a generic component.

Use **(a)**.

- [ ] **Step 2: Update `login-page.tsx`**

At the top of `frontend/src/app/components/login-page.tsx`, add:

```tsx
import { useNavigate, useSearchParams } from 'react-router-dom';
```

Inside `LoginPage`, near the other `useState` hooks, add:

```tsx
const navigate = useNavigate();
const [searchParams] = useSearchParams();
```

Define a safe-next helper at the top of the file (above the component):

```tsx
function safeNext(raw: string | null): string {
  if (!raw) return '/';
  // Only allow relative same-origin paths to avoid open-redirect.
  if (!raw.startsWith('/') || raw.startsWith('//')) return '/';
  return raw;
}
```

In `handleLogin`, after `await login({...})` and `toast.success(...)`, add:

```tsx
const target = safeNext(searchParams.get('next'));
navigate(target, { replace: true });
```

- [ ] **Step 3: Verify it compiles**

```bash
cd frontend && yarn tsc --noEmit
```
Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/app/components/login-page.tsx
git commit -m "feat(auth): login honors ?next= for safe relative paths"
```

---

### Task 15: End-to-end manual verification

The frontend has no test framework, so verify the round-trip by hand.

- [ ] **Step 1: Start the dev stack**

```bash
make dev
```
Wait until both backend (`runserver`) and frontend (`vite`) are up.

- [ ] **Step 2: Register a test MCP client**

In a separate terminal:

```bash
curl -s -X POST http://localhost:8000/oauth/register \
  -H 'Content-Type: application/json' \
  -d '{"client_name":"Test","redirect_uris":["http://localhost:9999/cb"]}' | tee /tmp/mcp_client.json
```
Note the `client_id`.

- [ ] **Step 3: Build the OAuth authorize URL**

In the browser, log in to Poupix (so the SPA has a JWT). Then open:

```
http://localhost:8000/oauth/authorize?client_id=<CID>&redirect_uri=http%3A%2F%2Flocalhost%3A9999%2Fcb&code_challenge=AAAA&code_challenge_method=S256&scope=mcp%3Aread&state=abc
```

Expected: browser 302s to `http://localhost:5173/oauth/authorize?...`, the consent screen renders with "Autorizar Test", and the "Autorizar" button is enabled.

- [ ] **Step 4: Click "Negar"**

Expected: browser navigates to `http://localhost:9999/cb?error=access_denied&state=abc` (will 404 since nothing serves that port — confirm the URL in the address bar).

- [ ] **Step 5: Repeat with a real PKCE challenge and click "Autorizar"**

Generate a verifier/challenge pair (Python REPL: `import secrets, hashlib, base64; v=secrets.token_urlsafe(32); c=base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b'=').decode(); print(v, c)`). Use the challenge in the URL. Click "Autorizar". Expected: browser navigates to `http://localhost:9999/cb?code=...&state=abc`.

- [ ] **Step 6: Verify the unauthenticated path**

Log out of Poupix. Open the same `/oauth/authorize` URL on the backend. Expected: 302 to SPA → SPA redirects to `/login?next=%2Foauth%2Fauthorize%3F...`. After logging in, you land back on the consent screen.

- [ ] **Step 7: Verify the integrations page still works**

Navigate to `/integracoes`. Expected: connection list loads (200, not 302). The "Test" client from Step 2 should appear if you completed Step 5. Click "Revogar". Expected: row disappears, toast shows success.

- [ ] **Step 8: Verify with mismatched `redirect_uri`**

Open `/oauth/authorize` with `redirect_uri=https://evil.example.com/cb`. Expected: consent screen renders the "URL de retorno não permitida" banner and the Autorizar button is disabled.

No commit needed for Task 15 — it's verification only.

---

## Final regression check

- [ ] Run the full OAuth test suite one more time:

```bash
cd backend && MCP_PG_INTEGRATION=1 pytest modules/ai/mcp/oauth/ -v
```
Expected: all tests pass.

- [ ] TypeScript check the whole frontend:

```bash
cd frontend && yarn tsc --noEmit
```
Expected: no errors introduced by this plan.

---

## Notes / pitfalls

- **`MCP_OAUTH_FRONTEND_URL` in prod** must be set to the SPA's origin (e.g. `https://app.poupix.connectakit.com.br`). If `MCP_OAUTH_FRONTEND_URL` and `MCP_OAUTH_ISSUER` point at different hosts, CORS for `/api/v1/mcp/oauth/*` already works because `CORS_ALLOW_ALL_ORIGINS = True` (see `infra/settings.py`).
- **JWT method name on `JWTGateway`:** the plan assumes `create_access_token(user_id=...)`. Confirm in Task 6, Step 1. If the actual name differs, swap it everywhere in the test code (Tasks 6, 8, 9).
- **`apiRequest` and 401:** existing code in `frontend/src/services/client.ts` treats 403 as expired-token (refresh + retry) and any other non-2xx as a generic error. The new public client-info endpoint returns 404 for unknown clients; the consent page handles that by showing the "Aplicativo não reconhecido" card. 401 from the authorize endpoint becomes a generic error toast — acceptable.
- **CSRF:** the JSON authorize and revoke endpoints are `@csrf_exempt` (matching the rest of the OAuth views). They're protected by JWT, not session cookies.
