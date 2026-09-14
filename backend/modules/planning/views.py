from rest_framework import decorators, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from modules.planning.container import PlanningContainer
from modules.userdata.authentication import JWTAuthentication


class PurchaseIntentionViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = PlanningContainer()

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
        intention = self.container.update_intention_use_case().execute(
            pk, request.data, request.user.id
        )
        return Response(intention, status=status.HTTP_200_OK)

    def destroy(self, request, pk: str):
        self.container.delete_intention_use_case().execute(pk, request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=True, methods=["POST"])
    def convert(self, request, pk: str):
        intention = self.container.convert_intention_use_case().execute(
            pk, request.data, request.user.id
        )
        return Response(intention, status=status.HTTP_200_OK)
