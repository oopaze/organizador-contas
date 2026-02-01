from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin

from modules.userdata.authentication import JWTAuthentication
from modules.file_reader.container import FileReaderContainer
from modules.ai.container import AIContainer
from modules.ai.types import LlmModels


class UploadFileView(APIView):
    parser_classes = [MultiPartParser]
    authentication_classes = [JWTAuthentication]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ask_use_case = AIContainer().ask_use_case()
        self.container = FileReaderContainer(ask_use_case=ask_use_case)

    def post(self, request: Request) -> Response:
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        password = request.data.get("password")
        model = request.data.get("model", LlmModels.DEEPSEEK_CHAT.name)
        try:
            self.container.upload_file_use_case().execute(file, request.user.id, password, model=model)
            return Response(
                {"message": "File uploaded successfully"},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UploadSheetView(APIView):
    parser_classes = [MultiPartParser]
    authentication_classes = [JWTAuthentication]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ask_use_case = AIContainer().ask_use_case()
        self.container = FileReaderContainer(ask_use_case=ask_use_case)

    def post(self, request: Request) -> Response:
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        model = request.data.get("model", LlmModels.DEEPSEEK_CHAT.name)
        try:
            result = self.container.upload_sheet_use_case().execute(file, request.user.id, model=model)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class BillViewSet(ViewSetMixin, APIView):
    authentication_classes = [JWTAuthentication]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = FileReaderContainer()

    def list(self, request: Request) -> Response:
        bills = self.container.list_bills_use_case().execute()
        return Response(bills, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, pk: str) -> Response:
        bill = self.container.load_bills_with_transactions_use_case().execute(pk)
        return Response(bill, status=status.HTTP_200_OK)
