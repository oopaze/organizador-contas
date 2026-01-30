from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from modules.ai.chat.container import AIChatContainer
from modules.ai.container import AIContainer
from modules.userdata.authentication import JWTAuthentication
from modules.transactions.container import TransactionsContainer


class StartConversionView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_container(self):
        ai_container = AIContainer()
        ask_use_case = ai_container.ask_use_case()
        create_embedding_use_case = ai_container.create_embedding_use_case()
        tools = TransactionsContainer(user_id=self.request.user.id).get_tools_for_ai_use_case().execute()

        return AIChatContainer(
            ask_use_case=ask_use_case, 
            create_embedding_use_case=create_embedding_use_case, 
            tools=tools
        )

    def post(self, request):
        data = request.data
        data["user"] = request.user.id

        container = self.get_container()
        result = container.start_conversion_use_case().execute(data)
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

    def get_container(self):
        ai_container = AIContainer()
        ask_use_case = ai_container.ask_use_case()
        create_embedding_use_case = ai_container.create_embedding_use_case()
        tools = TransactionsContainer(user_id=self.request.user.id).get_tools_for_ai_use_case().execute()

        return AIChatContainer(
            ask_use_case=ask_use_case, 
            create_embedding_use_case=create_embedding_use_case, 
            tools=tools
        )

    def post(self, request, conversation_id):
        user_id = request.user.id
        content = request.data["content"]
        container = self.get_container()
        result = container.send_conversion_message_use_case().execute(conversation_id, content, user_id)
        return Response(result, status=status.HTTP_200_OK)
