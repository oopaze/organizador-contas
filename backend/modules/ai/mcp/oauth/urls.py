from django.urls import path

from modules.ai.mcp.oauth import views


urlpatterns = [
    path("oauth/register", views.register_client, name="mcp_oauth_register"),
    path("oauth/authorize", views.authorize, name="mcp_oauth_authorize"),
    path("oauth/token", views.token, name="mcp_oauth_token"),
    path("oauth/revoke", views.revoke, name="mcp_oauth_revoke"),
    path(".well-known/oauth-authorization-server", views.well_known_authorization_server),
    path(".well-known/oauth-protected-resource", views.well_known_protected_resource),
    path("api/v1/mcp/oauth/client/<str:client_id>/", views.mcp_client_info, name="mcp_oauth_client_info"),
    path("api/v1/mcp/connections/", views.list_connections, name="mcp_list_connections"),
    path("api/v1/mcp/connections/<str:client_id>/revoke/", views.revoke_connection, name="mcp_revoke_connection"),
]
