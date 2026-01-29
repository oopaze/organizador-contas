from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from modules.ai.chat.container import AIChatContainer
from modules.ai.container import AIContainer
from modules.userdata.authentication import JWTAuthentication


class StartConversionView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ask_use_case = AIContainer().ask_use_case()
        self.container = AIChatContainer(ask_use_case=ask_use_case)

    def post(self, request):
        data = request.data
        data["user"] = request.user.id

        result = self.container.start_conversion_use_case().execute(data)
        return Response(result, status=status.HTTP_200_OK)


class ListConversationsView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = AIChatContainer()

    def get(self, request):
        user_id = request.user.id
        result = self.container.list_conversations_use_case().execute(user_id)
        return Response(result, status=status.HTTP_200_OK)
    

class ListMessagesView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = AIChatContainer()

    def get(self, request, conversation_id):
        user_id = request.user.id
        result = self.container.list_messages_use_case().execute(conversation_id, user_id)
        return Response(result, status=status.HTTP_200_OK)


class SendConversionMessageView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ask_use_case = AIContainer().ask_use_case()
        self.container = AIChatContainer(ask_use_case=ask_use_case)

    def post(self, request, conversation_id):
        user_id = request.user.id
        content = request.data["content"]
        result = self.container.send_conversion_message_use_case().execute(conversation_id, content, user_id)
        return Response(result, status=status.HTTP_200_OK)
