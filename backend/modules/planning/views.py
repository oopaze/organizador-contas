from rest_framework import decorators, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.ai.container import AIContainer
from modules.planning.container import PlanningContainer
from modules.userdata.authentication import JWTAuthentication


class ProjectionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = PlanningContainer()

    def get(self, request: Request) -> Response:
        try:
            result = self.container.projection_use_case().execute(
                request.user.id,
                start=request.query_params.get("start"),
                end=request.query_params.get("end"),
            )
        except ValueError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)


class PurchaseIntentionViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ai_container = AIContainer()
        self.container = PlanningContainer(
            ask_use_case=ai_container.ask_use_case(),
            ai_call_repository=ai_container.ai_call_repository(),
        )

    def list(self, request):
        intentions = self.container.list_intentions_use_case().execute(
            request.user.id,
            month=request.query_params.get("month"),
            start=request.query_params.get("start"),
            end=request.query_params.get("end"),
            status=request.query_params.get("status"),
        )
        return Response(intentions, status=status.HTTP_200_OK)

    def create(self, request):
        intention = self.container.create_intention_use_case().execute(
            request.data, request.user.id
        )
        return Response(intention, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str):
        try:
            intention = self.container.update_intention_use_case().execute(
                pk, request.data, request.user.id
            )
        except ValueError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(intention, status=status.HTTP_200_OK)

    def destroy(self, request, pk: str):
        try:
            self.container.delete_intention_use_case().execute(pk, request.user.id)
        except ValueError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=True, methods=["POST"])
    def convert(self, request, pk: str):
        try:
            intention = self.container.convert_intention_use_case().execute(
                pk, request.data, request.user.id
            )
        except ValueError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(intention, status=status.HTTP_200_OK)
