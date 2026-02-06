from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from modules.ai.container import AIContainer
from modules.userdata.authentication import JWTAuthentication

class ListAICallsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = AIContainer()

    def get(self, request: Request):
        user_id = request.user.id
        filter_by_model = request.query_params.get("model")
        due_date_start = request.query_params.get("due_date_start")
        due_date_end = request.query_params.get("due_date_end")

        ai_calls = self.container.list_ai_calls_use_case().execute(user_id, filter_by_model, due_date_start, due_date_end)
        return Response(ai_calls, status=status.HTTP_200_OK)


class StatsAICallsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = AIContainer()

    def get(self, request: Request):
        user_id = request.user.id
        filter_by_model = request.query_params.get("model")
        due_date_start = request.query_params.get("due_date_start")
        due_date_end = request.query_params.get("due_date_end")

        stats = self.container.stats_ai_call_use_case().execute(user_id, filter_by_model, due_date_start, due_date_end)
        return Response(stats, status=status.HTTP_200_OK)
    

class ListEmbeddingsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = AIContainer()

    def get(self, request: Request):
        user_id = request.user.id
        due_date_start = request.query_params.get("due_date_start")
        due_date_end = request.query_params.get("due_date_end")

        embeddings = self.container.list_embeddings_use_case().execute(user_id, due_date_start, due_date_end)
        return Response(embeddings, status=status.HTTP_200_OK)


class StatsEmbeddingsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = AIContainer()

    def get(self, request: Request):
        user_id = request.user.id
        due_date_start = request.query_params.get("due_date_start")
        due_date_end = request.query_params.get("due_date_end")

        stats = self.container.stats_embeddings_use_case().execute(user_id, due_date_start, due_date_end)
        return Response(stats, status=status.HTTP_200_OK)
