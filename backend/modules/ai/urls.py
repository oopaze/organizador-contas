from django.urls import include, path

urlpatterns = [
    path("chat/", include("modules.ai.chat.urls")),
]
