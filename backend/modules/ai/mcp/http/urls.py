from django.urls import path

from modules.ai.mcp.http import views


urlpatterns = [
    path("mcp", views.mcp_endpoint, name="mcp_endpoint"),
]
