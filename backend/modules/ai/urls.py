from django.urls import include, path

from modules.ai.views import ListAICallsView, StatsAICallsView, ListEmbeddingsView, StatsEmbeddingsView

urlpatterns = [
    path("chat/", include("modules.ai.chat.urls")),
    path("ai-calls/", ListAICallsView.as_view(), name="list_ai_calls"),
    path("ai-calls/stats/", StatsAICallsView.as_view(), name="stats_ai_calls"),
    path("embeddings/", ListEmbeddingsView.as_view(), name="list_embeddings"),
    path("embeddings/stats/", StatsEmbeddingsView.as_view(), name="stats_embeddings"),
]
