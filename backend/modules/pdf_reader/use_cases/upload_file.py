from django.core.files.uploadedfile import UploadedFile

from modules.pdf_reader.factories.ai_call import AICallFactory
from modules.pdf_reader.factories.file import FileFactory
from modules.pdf_reader.gateways.google_llm import GoogleLLMGateway
from modules.pdf_reader.repositories.ai_call import AICallRepository
from modules.pdf_reader.repositories.file import FileRepository
from modules.pdf_reader.serializers.file import FileSerializer
from modules.pdf_reader.use_cases.transpose_file_bill_to_models import TransposeFileBillToModelsUseCase

PROMPT = """
You will receive as input a PDF file containing a CREDIT CARD STATEMENT.

Your task is ONLY to extract and organize the explicit data that represents actual financial movements and the current bill status. 
DO NOT extract marketing offers, future installment simulations, or credit limit summaries.

1. BASIC STATEMENT INFORMATION
Extract only:
- [cite_start]bill_identifier: Card name/bank (e.g., "C&A VISA GOLD") [cite: 2, 144]
- [cite_start]total_amount: Total amount due for the current month (float) [cite: 4, 149]
- [cite_start]due_date: Due date in YYYY-MM-DD format [cite: 6, 150]

2. TRANSACTIONS (VALID MOVEMENTS ONLY)
[cite_start]List ALL real transactions located in the "Lançamentos" or "Transações" section. 
[cite_start]IGNORE sections like "Parcelamento da fatura" (simulations), "Limites", or "Próxima Fatura"[cite: 112, 113, 143].

For each valid transaction (purchases, fees, payments, credits), extract:
- [cite_start]date: Include the statement year (YYYY-MM-DD) [cite: 76, 107]
- [cite_start]description: Text exactly as it appears [cite: 107]
- [cite_start]amount: Float value (negative for payments/credits) [cite: 107]
- [cite_start]installment_info: Use "installment X of Y" if present (e.g., 03/10); otherwise "not installment" [cite: 107]

Mandatory formatting rules:
- Response MUST be a single, valid JSON object.
- DO NOT include "created_at", "updated_at", or internal IDs.
- NO extra text, comments, or explanations.
- All numeric values must be directly parseable (dots for decimals, no currency symbols).

Response format:
{
  "bill_identifier": "string",
  "total_amount": 0.00,
  "due_date": "YYYY-MM-DD",
  "transactions": [
    {
      "date": "YYYY-MM-DD",
      "description": "string",
      "amount": 0.00,
      "installment_info": "string"
    }
  ]
}
"""


class UploadFileUseCase:
    def __init__(
        self,
        file_repository: FileRepository,
        file_factory: FileFactory,
        google_llm_gateway: GoogleLLMGateway,
        file_serializer: FileSerializer,
        transpose_file_bill_to_models_use_case: TransposeFileBillToModelsUseCase,
        ai_call_repository: AICallRepository,
        ai_call_factory: AICallFactory,
    ):
        self.file_repository = file_repository
        self.file_factory = file_factory
        self.google_llm_gateway = google_llm_gateway
        self.file_serializer = file_serializer
        self.transpose_file_bill_to_models_use_case = transpose_file_bill_to_models_use_case
        self.ai_call_repository = ai_call_repository
        self.ai_call_factory = ai_call_factory

    def execute(self, file: UploadedFile, user_id: int):
        uploaded_file = self.file_factory.build(file)
        saved_file = self.file_repository.create(uploaded_file)
        pdf_text = saved_file.extract_text_from_pdf()

        prompt = [PROMPT, f"Here is the PDF content: {pdf_text}"] 
        response = self.google_llm_gateway.ask(prompt=prompt)
        ai_call = self.ai_call_repository.create(
            self.ai_call_factory.build_from_ai_response(
                prompt, response
            )
        )

        saved_file.update_ai_info(ai_call)
        updated_file = self.file_repository.update(saved_file)
        self.transpose_file_bill_to_models_use_case.execute(updated_file.id, user_id)
        
        return self.file_serializer.serialize(updated_file)
