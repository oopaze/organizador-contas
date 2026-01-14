from rest_framework import status, viewsets
from rest_framework.response import Response

from modules.userdata.authentication import JWTAuthentication
from modules.transactions.container import TransactionsContainer


class ActorViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = TransactionsContainer()

    def list(self, request):
        actors = self.container.list_actors_use_case().execute()
        return Response(actors, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk: str):
        actor = self.container.get_actor_use_case().execute(pk)
        return Response(actor, status=status.HTTP_200_OK)
    
    def create(self, request):
        name = request.data.get("name")
        actor = self.container.create_actor_use_case().execute(name)
        return Response(actor, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk: str):
        name = request.data.get("name")
        actor = self.container.update_actor_use_case().execute(pk, name)
        return Response(actor, status=status.HTTP_200_OK)
    
    def destroy(self, request, pk: str):
        self.container.delete_actor_use_case().execute(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class TransactionViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

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


class SubTransactionViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = TransactionsContainer()

    def list(self, request):
        sub_transactions = self.container.list_sub_transactions_use_case().execute()
        return Response(sub_transactions, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk: str):
        sub_transaction = self.container.get_sub_transaction_use_case().execute(pk)
        return Response(sub_transaction, status=status.HTTP_200_OK)
    
    def create(self, request):
        data = request.data
        sub_transaction = self.container.create_sub_transaction_use_case().execute(data)
        return Response(sub_transaction, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk: str):
        data = request.data
        sub_transaction = self.container.update_sub_transaction_use_case().execute(pk, data)
        return Response(sub_transaction, status=status.HTTP_200_OK)
    
    def destroy(self, request, pk: str):
        self.container.delete_sub_transaction_use_case().execute(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
