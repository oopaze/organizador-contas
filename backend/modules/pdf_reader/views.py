from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin

from modules.userdata.authentication import JWTAuthentication
from modules.pdf_reader.container import PDFReaderContainer


class UploadFileView(APIView):
    parser_classes = [MultiPartParser]
    authentication_classes = [JWTAuthentication]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = PDFReaderContainer()

    def post(self, request: Request) -> Response:
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.container.upload_file_use_case().execute(file, request.user.id)
        return Response(
            {"message": "File uploaded successfully"},
            status=status.HTTP_201_CREATED,
        )


class BillViewSet(ViewSetMixin, APIView):
    authentication_classes = [JWTAuthentication]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = PDFReaderContainer()

    def list(self, request: Request) -> Response:
        bills = self.container.list_bills_use_case().execute()
        return Response(bills, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, pk: str) -> Response:
        bill = self.container.load_bills_with_transactions_use_case().execute(pk)
        return Response(bill, status=status.HTTP_200_OK)
