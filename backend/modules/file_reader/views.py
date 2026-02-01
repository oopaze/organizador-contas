import logging
import time
import traceback

from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin

from modules.userdata.authentication import JWTAuthentication
from modules.file_reader.container import FileReaderContainer
from modules.ai.container import AIContainer

logger = logging.getLogger(__name__)


class UploadFileView(APIView):
    parser_classes = [MultiPartParser]
    authentication_classes = [JWTAuthentication]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ask_use_case = AIContainer().ask_use_case()
        self.container = FileReaderContainer(ask_use_case=ask_use_case)

    def post(self, request: Request) -> Response:
        logger.info("UploadFileView.post - Starting file upload for user: %s", request.user.id)

        file = request.FILES.get("file")
        if not file:
            logger.warning("UploadFileView.post - No file provided")
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info("UploadFileView.post - File: %s, Size: %s bytes, Content-Type: %s",
                    file.name, file.size, file.content_type)

        password = request.data.get("password")
        has_password = bool(password)
        logger.info("UploadFileView.post - Has password: %s", has_password)

        start_time = time.time()
        try:
            result = self.container.upload_file_use_case().execute(file, request.user.id, password)
            elapsed = time.time() - start_time
            logger.info("UploadFileView.post - SUCCESS in %.2fs - File: %s", elapsed, file.name)
            return Response(
                {"message": "File uploaded successfully"},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error("UploadFileView.post - ERROR after %.2fs - File: %s, Error: %s",
                         elapsed, file.name, str(e))
            logger.error("UploadFileView.post - Traceback:\n%s", traceback.format_exc())
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
