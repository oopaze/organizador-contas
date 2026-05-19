import logging
import traceback

from rest_framework import status, viewsets, decorators
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from modules.ai.container import AIContainer
from modules.ai.types import LlmModels
from modules.file_reader.container import FileReaderContainer
from modules.file_reader.exceptions import InvalidPasswordException
from modules.loans.container import LoansContainer
from modules.loans.use_cases.loan_payment.upload_pix_receipt import (
    PixReceiptParseError,
    UploadPixReceiptUseCase,
)
from modules.userdata.authentication import JWTAuthentication

logger = logging.getLogger(__name__)


class LoanViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ai = AIContainer()
        self.container = LoansContainer(
            ask_use_case=ai.ask_use_case(),
            ai_call_repository=ai.ai_call_repository(),
        )

    def list(self, request):
        filters = {}
        if request.query_params.get("actor_id"):
            filters["actor_id"] = request.query_params["actor_id"]
        if request.query_params.get("status"):
            filters["status"] = request.query_params["status"]
        loans = self.container.list_loans_use_case().execute(request.user.id, filters)
        return Response(loans, status=status.HTTP_200_OK)

    def retrieve(self, request, pk: str):
        loan = self.container.get_loan_use_case().execute(pk, request.user.id)
        return Response(loan, status=status.HTTP_200_OK)

    def create(self, request):
        loan = self.container.create_loan_use_case().execute(request.data, request.user.id)
        return Response(loan, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk: str):
        loan = self.container.update_loan_use_case().execute(pk, request.data, request.user.id)
        return Response(loan, status=status.HTTP_200_OK)

    def destroy(self, request, pk: str):
        self.container.delete_loan_use_case().execute(pk, request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=False, methods=["GET"])
    def stats(self, request):
        data = self.container.loan_stats_use_case().execute(request.user.id)
        return Response(data, status=status.HTTP_200_OK)


class LoanPaymentViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ai = AIContainer()
        self.container = LoansContainer(
            ask_use_case=ai.ask_use_case(),
            ai_call_repository=ai.ai_call_repository(),
        )
        self.file_reader = FileReaderContainer()

    def list(self, request):
        payments = self.container.list_loan_payments_use_case().execute(
            user_id=request.user.id,
            loan_id=request.query_params.get("loan_id"),
            paid_at_month=int(request.query_params["paid_at__month"])
            if request.query_params.get("paid_at__month") else None,
            paid_at_year=int(request.query_params["paid_at__year"])
            if request.query_params.get("paid_at__year") else None,
        )
        return Response(payments, status=status.HTTP_200_OK)

    def retrieve(self, request, pk: str):
        payment = self.container.get_loan_payment_use_case().execute(pk, request.user.id)
        return Response(payment, status=status.HTTP_200_OK)

    def create(self, request):
        payment = self.container.create_loan_payment_use_case().execute(
            request.data, request.user.id
        )
        return Response(payment, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk: str):
        payment = self.container.update_loan_payment_use_case().execute(
            pk, request.data, request.user.id
        )
        return Response(payment, status=status.HTTP_200_OK)

    def destroy(self, request, pk: str):
        self.container.delete_loan_payment_use_case().execute(pk, request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=False, methods=["POST"], url_path="upload_receipt")
    def upload_receipt(self, request):
        file = request.FILES.get("file")
        loan_id = request.data.get("loan_id")
        model = request.data.get("model", LlmModels.GOOGLE_GEMINI_2_5_FLASH_LITE.name)
        password = request.data.get("password")

        if not file:
            return Response({"error": "Nenhum arquivo foi enviado."}, status=400)
        if not loan_id:
            return Response({"error": "loan_id é obrigatório."}, status=400)

        use_case = UploadPixReceiptUseCase(
            file_repository=self.file_reader.file_repository(),
            file_factory=self.file_reader.file_factory(),
            remove_pdf_password_use_case=self.file_reader.remove_pdf_password_use_case(),
            parse_pix_receipt_use_case=self.container.parse_pix_receipt_use_case(),
            create_loan_payment_use_case=self.container.create_loan_payment_use_case(),
            loan_repository=self.container.loan_repository(),
        )

        try:
            result = use_case.execute(
                file=file, loan_id=int(loan_id), user_id=request.user.id,
                model=model, password=password,
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except InvalidPasswordException:
            return Response({"error": "Senha inválida para o PDF"}, status=400)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
        except PixReceiptParseError as exc:
            return Response(
                {"error": exc.message, "file_id": exc.file_id},
                status=422,
            )
        except Exception:
            logger.error(traceback.format_exc())
            return Response({"error": "Erro ao processar o comprovante."}, status=500)
