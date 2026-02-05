
from django.core.files.uploadedfile import UploadedFile

from modules.file_reader.factories.ai_call import AICallFactory
from modules.file_reader.factories.file import FileFactory
from modules.file_reader.repositories.ai_call import AICallRepository
from modules.file_reader.repositories.file import FileRepository
from modules.file_reader.serializers.file import FileSerializer
from modules.file_reader.use_cases.transpose_file_bill_to_models import TransposeFileBillToModelsUseCase
from modules.ai.use_cases.ask import AskUseCase
from modules.file_reader.use_cases.remover_pdf_password import RemovePDFPasswordUseCase
from modules.ai.types import LlmModels

PROMPT = """
You will receive TEXT extracted from a PDF CREDIT CARD STATEMENT.

Your task is ONLY to extract explicit financial movements and the current bill status.
Do NOT infer, estimate, or guess any value.

IGNORE marketing offers, simulations, credit limits, and future statements.

If a field is not explicitly present, return null.

Extract:

1. BASIC STATEMENT INFORMATION
- bill_identifier: Card name or bank
- total_amount: Total amount due for the current month (ALWAYS POSITIVE float)
- due_date: Due date in YYYY-MM-DD format
- transaction_type: "incoming" if this is a credit card bill, "outgoing" otherwise

2. TRANSACTIONS
Extract ONLY real transactions listed under sections like
"Lançamentos" or "Transações".

IGNORE sections like:
"Parcelamento da fatura", "Limites", "Próxima Fatura".

For each transaction:
- date: YYYY-MM-DD (include statement year)
- description: Exact text
- amount: ALWAYS POSITIVE float (the value of the transaction)
- installment_info: "installment X of Y" or "not installment"

IMPORTANT RULES ABOUT AMOUNTS:
- ALL amounts must be POSITIVE numbers (e.g., 150.00, not -150.00)
- The amount represents the value of the bill/transaction
- If the PDF shows negative values, convert them to positive
- Credit card bills are expenses, so all transactions are outgoing by default

Formatting rules:
- Output MUST be a single valid JSON object
- No extra text or explanations
- Use "." as decimal separator
- No currency symbols

If no transactions exist, return an empty array.

Response format:
{
  "bill_identifier": "string",
  "total_amount": 150.00,
  "due_date": "YYYY-MM-DD",
  "transaction_type": "incoming" or "outgoing",
  "transactions": [
    {
      "date": "YYYY-MM-DD",
      "description": "string",
      "amount": 50.00,
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
        file_serializer: FileSerializer,
        transpose_file_bill_to_models_use_case: TransposeFileBillToModelsUseCase,
        ai_call_repository: AICallRepository,
        ai_call_factory: AICallFactory,
        ask_use_case: AskUseCase,
        remove_pdf_password_use_case: RemovePDFPasswordUseCase,
    ):
        self.file_repository = file_repository
        self.file_factory = file_factory
        self.file_serializer = file_serializer
        self.transpose_file_bill_to_models_use_case = transpose_file_bill_to_models_use_case
        self.ai_call_repository = ai_call_repository
        self.ai_call_factory = ai_call_factory
        self.ask_use_case = ask_use_case
        self.remove_pdf_password_use_case = remove_pdf_password_use_case

    def execute(
      self, 
      file: UploadedFile, 
      user_id: int, 
      password: str = None, 
      model = LlmModels.DEEPSEEK_CHAT.name,
      create_in_future_months: bool = False,
    ):
        uploaded_file = self.file_factory.build(file)
        saved_file = self.file_repository.create(uploaded_file, user_id)

        if password:
            file_path = self.remove_pdf_password_use_case.execute(saved_file, password)

        file_path = saved_file.uploaded_file.path
        pdf_text = saved_file.extract_text_from_pdf(file_path)

        prompt = [PROMPT, f"Here is the PDF content: {pdf_text}"]
        ai_call_id = self.ask_use_case.execute(prompt, response_format="json_object", model=model)

        ai_call = self.ai_call_repository.get(ai_call_id)
        saved_file.update_ai_info(ai_call)
        updated_file = self.file_repository.update(saved_file)

        self.transpose_file_bill_to_models_use_case.execute(updated_file.id, user_id, create_in_future_months)
        return self.file_serializer.serialize(updated_file)
