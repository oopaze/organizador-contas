from django.urls import path

from modules.ai.mcp.oauth import views


urlpatterns = [
    path("oauth/register", views.register_client, name="mcp_oauth_register"),
    path("oauth/authorize", views.authorize, name="mcp_oauth_authorize"),
    path("oauth/token", views.token, name="mcp_oauth_token"),
    path("oauth/revoke", views.revoke, name="mcp_oauth_revoke"),
    path(".well-known/oauth-authorization-server", views.well_known_authorization_server),
    path(".well-known/oauth-protected-resource", views.well_known_protected_resource),
]
