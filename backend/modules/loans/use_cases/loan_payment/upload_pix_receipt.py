from django.db import transaction

from modules.file_reader.factories.file import FileFactory
from modules.file_reader.repositories.file import FileRepository
from modules.file_reader.use_cases.remover_pdf_password import RemovePDFPasswordUseCase
from modules.loans.repositories.loan import LoanRepository
from modules.loans.use_cases.loan_payment.create import CreateLoanPaymentUseCase
from modules.loans.use_cases.parse_pix_receipt import ParsePixReceiptUseCase


class PixReceiptParseError(Exception):
    def __init__(self, message: str, file_id: int | None):
        super().__init__(message)
        self.message = message
        self.file_id = file_id


class UploadPixReceiptUseCase:
    def __init__(
        self,
        file_repository: FileRepository,
        file_factory: FileFactory,
        remove_pdf_password_use_case: RemovePDFPasswordUseCase,
        parse_pix_receipt_use_case: ParsePixReceiptUseCase,
        create_loan_payment_use_case: CreateLoanPaymentUseCase,
        loan_repository: LoanRepository,
    ):
        self.file_repository = file_repository
        self.file_factory = file_factory
        self.remove_pdf_password_use_case = remove_pdf_password_use_case
        self.parse_pix_receipt_use_case = parse_pix_receipt_use_case
        self.create_loan_payment_use_case = create_loan_payment_use_case
        self.loan_repository = loan_repository

    @transaction.atomic
    def execute(self, file, loan_id: int, user_id: int, model: str, password: str | None = None) -> dict:
        loan = self.loan_repository.get(loan_id, user_id)
        if loan.status != "active":
            raise ValueError("Empréstimo não está ativo")

        file_domain = self.file_factory.build(file)
        saved_file = self.file_repository.create(file_domain, user_id)

        if password:
            self.remove_pdf_password_use_case.execute(saved_file, password)

        raw_text = saved_file.extract_text_from_pdf(password)

        try:
            extracted = self.parse_pix_receipt_use_case.execute(
                raw_text=raw_text,
                file_name=file.name,
                user_id=user_id,
                model=model,
            )
        except ValueError as exc:
            raise PixReceiptParseError(str(exc), file_id=saved_file.id) from exc

        payment = self.create_loan_payment_use_case.execute(
            {
                "loan_id": loan_id,
                "amount": extracted["amount"],
                "paid_at": extracted["paid_at"],
                "note": extracted.get("transaction_id") or "",
                "file_id": saved_file.id,
            },
            user_id=user_id,
        )

        return {"payment": payment, "extracted": extracted}
