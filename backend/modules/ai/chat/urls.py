from django.urls import path

from modules.ai.chat.views import StartConversionView, ListConversationsView, ListMessagesView, SendConversionMessageView

urlpatterns = [
    path("start/", StartConversionView.as_view(), name="start_chat"),
    path("list/", ListConversationsView.as_view(), name="list_conversations"),
    path("<int:conversation_id>/messages", ListMessagesView.as_view(), name="list_messages"),
    path("<int:conversation_id>/ask", SendConversionMessageView.as_view(), name="send_message"),
]
