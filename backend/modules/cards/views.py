from rest_framework import decorators, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from modules.cards.container import CardsContainer
from modules.cards.models import Card
from modules.userdata.authentication import JWTAuthentication


class CardViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = CardsContainer()

    def list(self, request):
        return Response(self.container.list_cards_use_case().execute(request.user.id), status=status.HTTP_200_OK)

    def create(self, request):
        try:
            card = self.container.create_card_use_case().execute(request.data, request.user.id)
        except ValueError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(card, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk: str):
        try:
            card = self.container.update_card_use_case().execute(pk, request.data, request.user.id)
        except Card.DoesNotExist:
            return Response({"error": "Cartão não encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(card, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["POST"], url_path="set_active")
    def set_active(self, request, pk: str):
        try:
            card = self.container.set_card_active_use_case().execute(
                pk, request.data.get("is_active", False), request.user.id
            )
        except Card.DoesNotExist:
            return Response({"error": "Cartão não encontrado"}, status=status.HTTP_404_NOT_FOUND)
        return Response(card, status=status.HTTP_200_OK)
