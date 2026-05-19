from decimal import Decimal
from datetime import date
from unittest.mock import Mock, MagicMock, patch

from django.test import SimpleTestCase

from modules.loans.domains.loan import LoanDomain
from modules.loans.use_cases.loan_payment.upload_pix_receipt import (
    PixReceiptParseError,
    UploadPixReceiptUseCase,
)


@patch("django.db.transaction.Atomic.__enter__", return_value=None)
@patch("django.db.transaction.Atomic.__exit__", return_value=False)
class TestUploadPixReceiptUseCase(SimpleTestCase):
    def setUp(self):
        self.file_repo = Mock()
        self.file_factory = Mock()
        self.remove_password = Mock()
        self.parse_pix = Mock()
        self.create_payment = Mock()
        self.loan_repo = Mock()

        self.use_case = UploadPixReceiptUseCase(
            file_repository=self.file_repo,
            file_factory=self.file_factory,
            remove_pdf_password_use_case=self.remove_password,
            parse_pix_receipt_use_case=self.parse_pix,
            create_loan_payment_use_case=self.create_payment,
            loan_repository=self.loan_repo,
        )

    def _setup_active_loan(self):
        self.loan_repo.get.return_value = LoanDomain(
            id=42, user_id=7, actor_id=10,
            principal_amount=Decimal("5000"),
            lent_at=date(2026, 1, 1),
            status="active",
        )

    def _setup_file(self):
        saved = MagicMock()
        saved.id = 99
        saved.extract_text_from_pdf.return_value = "raw pdf text"
        self.file_factory.build.return_value = Mock()
        self.file_repo.create.return_value = saved
        return saved

    def test_happy_path_creates_payment_with_file_link(self, _exit, _enter):
        self._setup_active_loan()
        saved_file = self._setup_file()
        self.parse_pix.execute.return_value = {
            "amount": Decimal("1000.00"),
            "paid_at": date(2026, 3, 15),
            "transaction_id": "E12345",
        }
        self.create_payment.execute.return_value = {"id": 5, "loan_id": 42}

        fake_upload = Mock()
        fake_upload.name = "comprovante.pdf"

        result = self.use_case.execute(
            file=fake_upload, loan_id=42, user_id=7,
            model="gemini-2.5-flash-lite", password=None,
        )

        self.remove_password.execute.assert_not_called()
        saved_file.extract_text_from_pdf.assert_called_once_with(None)
        self.create_payment.execute.assert_called_once_with(
            {
                "loan_id": 42,
                "amount": Decimal("1000.00"),
                "paid_at": date(2026, 3, 15),
                "note": "E12345",
                "file_id": 99,
            },
            user_id=7,
        )
        self.assertEqual(result["payment"], {"id": 5, "loan_id": 42})
        self.assertEqual(result["extracted"]["amount"], Decimal("1000.00"))

    def test_rejects_inactive_loan(self, _exit, _enter):
        self.loan_repo.get.return_value = LoanDomain(
            id=42, user_id=7, actor_id=10,
            principal_amount=Decimal("5000"),
            lent_at=date(2026, 1, 1),
            status="cancelled",
        )
        fake_upload = Mock()
        fake_upload.name = "x.pdf"

        with self.assertRaises(ValueError):
            self.use_case.execute(
                file=fake_upload, loan_id=42, user_id=7,
                model="gemini-2.5-flash-lite", password=None,
            )

    def test_parser_failure_keeps_file_and_reraises_with_file_id(self, _exit, _enter):
        self._setup_active_loan()
        saved_file = self._setup_file()
        self.parse_pix.execute.side_effect = ValueError("amount não encontrado")

        fake_upload = Mock()
        fake_upload.name = "x.pdf"

        with self.assertRaises(PixReceiptParseError) as cm:
            self.use_case.execute(
                file=fake_upload, loan_id=42, user_id=7,
                model="gemini-2.5-flash-lite", password=None,
            )
        self.assertEqual(cm.exception.file_id, 99)
        self.assertIn("amount", cm.exception.message)
        self.create_payment.execute.assert_not_called()

    def test_applies_password_when_given(self, _exit, _enter):
        self._setup_active_loan()
        saved_file = self._setup_file()
        self.parse_pix.execute.return_value = {
            "amount": Decimal("500.00"),
            "paid_at": date(2026, 3, 10),
            "transaction_id": None,
        }
        self.create_payment.execute.return_value = {"id": 1}
        fake_upload = Mock()
        fake_upload.name = "x.pdf"

        self.use_case.execute(
            file=fake_upload, loan_id=42, user_id=7,
            model="gemini-2.5-flash-lite", password="secret",
        )

        self.remove_password.execute.assert_called_once_with(saved_file, "secret")
        saved_file.extract_text_from_pdf.assert_called_once_with("secret")
