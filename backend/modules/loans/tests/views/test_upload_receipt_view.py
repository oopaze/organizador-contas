from decimal import Decimal
from datetime import date
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from modules.loans.models import Loan
from modules.transactions.models import Actor


User = get_user_model()


class UploadPixReceiptViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="t@t.com", password="x")
        self.client.force_authenticate(self.user)
        self.actor = Actor.objects.create(name="Amor", user=self.user)
        self.loan = Loan.objects.create(
            user=self.user,
            actor=self.actor,
            principal_amount=Decimal("5000"),
            lent_at=date(2026, 1, 1),
        )

    def test_returns_400_when_loan_id_missing(self):
        file = BytesIO(b"%PDF-1.4")
        file.name = "comprovante.pdf"
        response = self.client.post(
            "/loans/loan_payments/upload_receipt/",
            {"file": file},
            format="multipart",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("loan_id", response.json()["error"])

    @patch("modules.loans.views.UploadPixReceiptUseCase")
    def test_happy_path(self, MockUseCase):
        MockUseCase.return_value.execute.return_value = {
            "payment": {"id": 1, "loan_id": self.loan.id},
            "extracted": {"amount": "1000"},
        }

        file = BytesIO(b"%PDF-1.4")
        file.name = "comprovante.pdf"
        response = self.client.post(
            "/loans/loan_payments/upload_receipt/",
            {"file": file, "loan_id": self.loan.id, "model": "gemini-2.5-flash-lite"},
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["payment"]["id"], 1)
