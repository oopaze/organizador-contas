# MCP OAuth — move consent UI from backend to frontend

**Status:** Draft for review
**Date:** 2026-05-19
**Scope:** Replace the Django-rendered OAuth consent page with a React route, and bring the MCP connection-management endpoints in line with the rest of the API's JWT auth.

## Problem

When Claude or ChatGPT initiates the MCP OAuth flow, the user is sent to `GET /oauth/authorize?...`, which today is served by a Django template ([backend/modules/ai/mcp/oauth/templates/mcp_oauth/consent.html](../../../backend/modules/ai/mcp/oauth/templates/mcp_oauth/consent.html)) gated by `@login_required`. Two issues:

1. **The auth gate cannot succeed.** The app authenticates via JWT Bearer tokens stored in localStorage; there is no Django session cookie. `@login_required` redirects every visitor to `/`, so the OAuth flow silently fails.
2. **The page is off-brand.** Even if it worked, users would see raw HTML with inline CSS — nothing like the rest of Poupix.

The same `@login_required` is also on `list_connections` and `revoke_connection`, which means the integrations page's "Conexões ativas" card cannot load real data in production.

## Goal

Make the connection flow user-driven from the frontend:

- A polished React consent screen, served from the SPA, that authenticates with the existing JWT system.
- A stateless backend that exposes JSON endpoints for the OAuth authorize/deny decision.
- Connection list/revoke API endpoints aligned with the rest of `/api/v1/` (JWT-authenticated).

## Non-goals

- Changing how Claude (`claude://mcp/install?...` deeplink) or ChatGPT (manual URL paste) initiate the flow.
- Touching the OAuth model, PKCE handling, token issuance, or revocation logic.
- Adding scopes beyond the existing `mcp:read`.

## Design

### High-level flow

```
Claude / ChatGPT
   │
   ▼
GET https://api.poupix.../oauth/authorize?client_id=&redirect_uri=&state=&code_challenge=&code_challenge_method=&scope=
   │  (backend returns 302)
   ▼
https://app.poupix.../oauth/authorize?{same query string}
   │  (React route)
   ├── no JWT? → /login?next=/oauth/authorize?{query} → after login, back here
   ├── invalid client / mismatched redirect_uri? → render error state
   └── render consent screen
          │
          ├── user clicks "Autorizar"
          │      └── POST /api/v1/mcp/oauth/authorize/ (JWT)
          │             └── returns { redirect_to: "<redirect_uri>?code=&state=" }
          │      └── window.location.assign(redirect_to)
          └── user clicks "Negar"
                 └── window.location.assign("<redirect_uri>?error=access_denied&state=")
```

The MCP HTTP endpoint `/mcp`, the discovery documents `/.well-known/oauth-authorization-server` and `/.well-known/oauth-protected-resource`, the `/oauth/register`, `/oauth/token`, and `/oauth/revoke` endpoints stay exactly as they are — they are machine-to-machine and have no UI.

### Backend changes

**1. Replace `GET /oauth/authorize` with a 302 to the SPA.**
The view becomes a thin handler that forwards the query string to the frontend's `/oauth/authorize` route. No template, no `@login_required`. New setting `MCP_OAUTH_FRONTEND_URL` (defaults to a sensible value for dev; configured per env) controls the target host.

**2. Remove the POST handler for `/oauth/authorize` and the `consent.html` template.**
Both are superseded by the new JSON endpoint. Remove the `mcp_oauth/` templates directory and any `TEMPLATES['DIRS']` entries that point at it.

**3. New endpoint `GET /api/v1/mcp/oauth/client/<client_id>/`.**
Public (no auth required — the consent screen needs to display the client name before login finishes). Returns:

```json
{ "client_id": "...", "name": "Claude", "redirect_uris": ["https://..."] }
```

Returns 404 if the client does not exist. Implemented by reusing `OAuthContainer.client_repository().get_by_client_id()`.

**4. New endpoint `POST /api/v1/mcp/oauth/authorize/`.**
JWT-authenticated. Request body:

```json
{
  "client_id": "...",
  "redirect_uri": "...",
  "code_challenge": "...",
  "code_challenge_method": "S256",
  "scope": "mcp:read",
  "state": "..."
}
```

Calls the existing `AuthorizeUseCase` with `user_id=request.user.id`. On success, builds the redirect URL (`<redirect_uri>?code=<auth_code>&state=<state>`) using the same logic the old view used, and returns:

```json
{ "redirect_to": "<redirect_uri>?code=&state=" }
```

On `OAuthError`, returns 400 with `{ "error": "...", "error_description": "..." }` — the React route renders this as an inline error.

**5. Migrate connection-management endpoints to JWT auth.**
Convert `list_connections` and `revoke_connection` from `@login_required` (Django session) to the project's `JWTAuthentication` ([backend/modules/userdata/authentication.py](../../../backend/modules/userdata/authentication.py)). Match the auth style used by the rest of `/api/v1/` (DRF `APIView` if neighbors use DRF; otherwise a plain decorator that validates the Bearer token). Keep the response shape unchanged so [frontend/src/services/mcp/mcpConnections.ts](../../../frontend/src/services/mcp/mcpConnections.ts) keeps working.

### Frontend changes

**1. New page `frontend/src/app/pages/oauth-authorize-page.tsx`.**
Mounted at `/oauth/authorize` in [routes.tsx](../../../frontend/src/app/pages/routes.tsx). Behavior:

- On mount, read OAuth params from the URL (`useSearchParams`).
- If any required param is missing, render a clean error: "Solicitação de autorização inválida."
- Fetch client info via `GET /api/v1/mcp/oauth/client/<client_id>/`. While loading: skeleton. If 404: "Aplicativo não reconhecido."
- Use the existing `useAuth()` context. If not authenticated, redirect to `/login?next=` with the full current URL encoded.
- Validate that `redirect_uri` matches one of the client's `redirect_uris`. If not, render an error and do **not** show the approve button.
- Render the consent card: app name, requested scope ("Leitura das suas transações, categorias e atores."), "Autorizar" and "Negar" buttons. Reuse `Card`, `Button`, `Badge` from the design system.
- "Autorizar": POST to the new endpoint, then `window.location.assign(redirect_to)`. Show a loading spinner during the request. On error, surface the message inline.
- "Negar": `window.location.assign(\`${redirect_uri}?error=access_denied&state=${state}\`)` directly, no API call.

**2. Login redirect support.**
Today's [login page](../../../frontend/src/app/components/login-page.tsx) ignores a `?next=` query. Update it to honor `next` after successful login, falling back to `/` as it does today. This is small but needs to be done so the OAuth flow can round-trip through login.

**3. New service `frontend/src/services/mcp/oauthAuthorize.ts`.**
Two functions:

```ts
export async function fetchMCPClient(clientId: string): Promise<MCPClientInfo> { ... }
export async function approveMCPAuthorization(params: AuthorizeParams): Promise<{ redirect_to: string }> { ... }
```

Both go through the existing `apiRequest` helper. `fetchMCPClient` bypasses the JWT (the endpoint is public) — `apiRequest` already tolerates calls without a token.

**4. No changes to [integrations-page.tsx](../../../frontend/src/app/pages/integrations-page.tsx).** It continues to use the same connection-list service; the backend swap is transparent.

### Routing & auth wrinkles

- `/oauth/authorize` is a new top-level route. It is **not** wrapped in `<Layout>` (no sidebar/header) — the consent screen should feel like a focused, modal-style page, similar to login.
- It is **not** wrapped in `<ProtectedRoute>` either; the page handles its own auth check so it can preserve the OAuth query string through login. (A naive `<ProtectedRoute>` would lose the params.)
- The new `POST /api/v1/mcp/oauth/authorize/` endpoint must be CSRF-exempt (it's JWT-authenticated and called via `fetch` with a Bearer header — matches every other `/api/v1/` endpoint).

### Error states

| Condition | What the user sees |
|---|---|
| Missing/malformed OAuth params | "Solicitação de autorização inválida." with a "Voltar ao Poupix" link. |
| Unknown `client_id` | "Aplicativo não reconhecido." |
| `redirect_uri` doesn't match a registered URI | "URL de retorno não permitida para este aplicativo." Approve button hidden. |
| Network failure on approve | Inline error toast; consent card stays interactive. |
| Use case raises `OAuthError` | Inline error message from the API's `error_description`. |
| User not logged in | Redirect to `/login?next=...` preserving the query string. |

### Testing

**Backend (pytest):**
- `GET /oauth/authorize?...` returns 302 to `MCP_OAUTH_FRONTEND_URL/oauth/authorize?<query>`.
- `GET /api/v1/mcp/oauth/client/<id>/` returns 200 with name; 404 for unknown.
- `POST /api/v1/mcp/oauth/authorize/` happy path returns `redirect_to` containing `code` and `state`.
- `POST /api/v1/mcp/oauth/authorize/` with mismatched `redirect_uri` returns 400 with `error=invalid_request`.
- `POST /api/v1/mcp/oauth/authorize/` without JWT returns 401.
- `GET /api/v1/mcp/connections/` returns the user's connections when called with a valid JWT.
- `POST /api/v1/mcp/connections/<id>/revoke/` revokes and returns the count.

**Frontend (vitest + RTL, in line with existing tests):**
- Page reads query params and shows the client name after fetch.
- "Negar" redirects to `<redirect_uri>?error=access_denied&state=`.
- "Autorizar" posts and navigates to `redirect_to`.
- Unauthenticated visit redirects to `/login?next=...`.
- Invalid `redirect_uri` hides the approve button.

## Migration / rollout

1. Ship backend changes first (new endpoints + 302 from old endpoint). Old `/oauth/authorize` POST handler kept as a fallback for one release if any in-flight client is mid-flow; otherwise remove immediately — there are no production users for the broken flow yet.
2. Ship frontend route and service in the same release; the 302 from the backend assumes the SPA route exists.
3. Remove `mcp_oauth/consent.html` and its template dir entry only after the frontend route is live.

## Open items / assumptions

- **`MCP_OAUTH_FRONTEND_URL` value:** dev defaults to `http://localhost:5173`; prod to `https://app.poupix.connectakit.com.br` (or whatever the SPA host is — confirm during implementation).
- **CORS:** the new `/api/v1/mcp/oauth/*` endpoints will be called from the SPA's origin, which already has CORS set up for `/api/v1/*`; no new config expected. Verify during implementation.
- **Login `next` param shape:** the design assumes URL-encoded relative paths only. The login page must reject absolute URLs / external hosts to prevent open-redirect bugs.
