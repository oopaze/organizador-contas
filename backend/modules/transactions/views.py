from rest_framework import status, viewsets, decorators
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from modules.userdata.authentication import JWTAuthentication
from modules.transactions.container import TransactionsContainer


class ActorViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = TransactionsContainer()

    def list(self, request):
        due_date = request.query_params.get("due_date")
        actors = self.container.list_actors_use_case().execute(request.user.id, due_date)
        return Response(actors, status=status.HTTP_200_OK)

    def retrieve(self, request, pk: str):
        due_date = request.query_params.get("due_date")
        actor = self.container.get_actor_use_case().execute(pk, request.user.id, due_date)
        return Response(actor, status=status.HTTP_200_OK)

    def create(self, request):
        name = request.data.get("name")
        actor = self.container.create_actor_use_case().execute(name, request.user.id)
        return Response(actor, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str):
        name = request.data.get("name")
        actor = self.container.update_actor_use_case().execute(pk, name, request.user.id)
        return Response(actor, status=status.HTTP_200_OK)

    def destroy(self, request, pk: str):
        self.container.delete_actor_use_case().execute(pk, request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class TransactionViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = TransactionsContainer()

    def list(self, request):
        filters = {"user_id": request.user.id}

        if request.query_params.get("due_date__month"):
            filters["due_date__month"] = int(request.query_params.get("due_date__month"))

        if request.query_params.get("due_date__year"):
            filters["due_date__year"] = int(request.query_params.get("due_date__year"))

        if request.query_params.get("transaction_type"):
            filters["transaction_type"] = request.query_params.get("transaction_type")

        transactions = self.container.list_transactions_use_case().execute(filters)
        return Response(transactions, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk: str):
        transaction = self.container.get_transaction_use_case().execute(pk, request.user.id)
        return Response(transaction, status=status.HTTP_200_OK)
    
    def create(self, request):
        data = request.data
        data["user_id"] = request.user.id
        transaction = self.container.create_transaction_use_case().execute(data)
        return Response(transaction, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk: str):
        data = request.data
        data["user_id"] = request.user.id
        transaction = self.container.update_transaction_use_case().execute(pk, data)
        return Response(transaction, status=status.HTTP_200_OK)
    
    def destroy(self, request, pk: str):
        self.container.delete_transaction_use_case().execute(pk, request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @decorators.action(detail=False, methods=["GET"])
    def stats(self, request):
        due_date = request.query_params.get("due_date")
        stats = self.container.transaction_stats_use_case().execute(request.user.id, due_date)
        return Response(stats, status=status.HTTP_200_OK)


class SubTransactionViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = TransactionsContainer()

    def list(self, request):
        due_date = request.query_params.get("due_date")
        actor_id = request.query_params.get("actor_id")

        sub_transactions = self.container.list_sub_transactions_use_case().execute(request.user.id, due_date, actor_id)
        return Response(sub_transactions, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk: str):
        sub_transaction = self.container.get_sub_transaction_use_case().execute(pk, request.user.id)
        return Response(sub_transaction, status=status.HTTP_200_OK)
    
    def create(self, request):
        data = request.data
        sub_transaction = self.container.create_sub_transaction_use_case().execute(data, request.user.id)
        return Response(sub_transaction, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk: str):
        data = request.data
        sub_transaction = self.container.update_sub_transaction_use_case().execute(pk, data, request.user.id)
        return Response(sub_transaction, status=status.HTTP_200_OK)
    
    def destroy(self, request, pk: str):
        self.container.delete_sub_transaction_use_case().execute(pk, request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
