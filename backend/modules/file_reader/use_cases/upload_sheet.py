import logging

from django.core.files.uploadedfile import UploadedFile

from modules.file_reader.factories.ai_call import AICallFactory

logger = logging.getLogger(__name__)
from modules.file_reader.factories.file import FileFactory
from modules.file_reader.repositories.ai_call import AICallRepository
from modules.file_reader.repositories.file import FileRepository
from modules.file_reader.serializers.file import FileSerializer
from modules.file_reader.use_cases.transpose_file_bill_to_models import TransposeFileBillToModelsUseCase
from modules.ai.use_cases.ask import AskUseCase
from modules.ai.types import LlmModels


USER_PROVIDED_DESCRIPTION_PROMPT = """
This was some information that the user provided to help you understand the spreadsheet better: {user_provided_description}
"""


SPREADSHEET_PROMPT = """You are a financial data extraction assistant. Analyze the following spreadsheet data and extract transactions.

IMPORTANT: This is different from a credit card bill!
- Credit card bills = 1 bill with many sub-transactions (purchases)
- Spreadsheets = MULTIPLE independent transactions, each one is a separate bill

The spreadsheet may contain various formats of financial data:
- Personal expense tracking (simple lists with date, description, value)
- Bank statements
- Budget spreadsheets
- Any other financial record format

Your task is to intelligently identify and extract transactions from ANY format. Look for:
- Columns that represent dates (may be labeled as "Data", "Date", "Dia", "Quando", or similar)
- Columns that represent descriptions (may be labeled as "Descrição", "Description", "O que", "Item", "Compra", or similar)
- Columns that represent amounts/values (may be labeled as "Valor", "Value", "Amount", "Preço", "Gasto", "R$", or similar)
- If there are multiple sheets, analyze ALL of them - sheet names often contain important info (month, category, etc.)

For EACH transaction/expense found in the spreadsheet, create a SEPARATE bill object:
- bill_identifier: Description of the transaction (e.g., "Supermercado", "Netflix", "Aluguel")
- total_amount: The transaction amount as a POSITIVE float (always positive, represents the bill value)
- due_date: The transaction date in YYYY-MM-DD format
- is_income: Boolean - true if this is income/revenue, false if it's an expense/bill (default: false)
- transactions: Usually EMPTY array [] - only add sub-transactions if the item has installments or sub-items

When to use sub-transactions (transactions array):
- If an item is split into installments (e.g., "TV 12x"), create sub-transactions for each installment
- If an item has sub-items that need to be tracked separately
- Otherwise, leave transactions as an empty array []

IMPORTANT RULES ABOUT AMOUNTS:
- ALL amounts must be POSITIVE numbers (e.g., 150.00, not -150.00)
- The amount represents the value of the bill/transaction
- Use "is_income": true to mark income/revenue entries (salary, refunds, etc.)
- Use "is_income": false (or omit) for expenses/bills (this is the default)
- If the spreadsheet has negative values, convert them to positive

OTHER RULES:
- Return a JSON ARRAY of bills, NOT a single object
- Each row/item in the spreadsheet = one bill in the array
- Be flexible with column names - they may be in Portuguese or English
- Skip rows that don't look like transactions (headers, totals, empty rows)
- If dates are in DD/MM/YYYY or DD/MM format, convert to YYYY-MM-DD
- If only day/month available, assume current year (2026)
- Use "." as decimal separator, no currency symbols
- Output MUST be a valid JSON array

Response format:
[
  {
    "bill_identifier": "Supermercado Extra",
    "total_amount": 150.00,
    "due_date": "2026-01-15",
    "is_income": false,
    "transactions": []
  },
  {
    "bill_identifier": "Salário",
    "total_amount": 5000.00,
    "due_date": "2026-01-05",
    "is_income": true,
    "transactions": []
  },
  {
    "bill_identifier": "TV Samsung 12x",
    "total_amount": 2400.00,
    "due_date": "2026-01-20",
    "is_income": false,
    "transactions": [
      {"date": "2026-01-20", "description": "Parcela 1/12", "amount": 200.00, "installment_info": "1 of 12"},
      {"date": "2026-02-20", "description": "Parcela 2/12", "amount": 200.00, "installment_info": "2 of 12"}
    ]
  }
]
"""


class UploadSheetUseCase:
    def __init__(
        self,
        ask_use_case: AskUseCase,
        file_repository: FileRepository,
        file_factory: FileFactory,
        file_serializer: FileSerializer,
        ai_call_repository: AICallRepository,
        ai_call_factory: AICallFactory,
        transpose_file_bill_to_models_use_case: TransposeFileBillToModelsUseCase,
    ):
        self.ask_use_case = ask_use_case
        self.file_repository = file_repository
        self.file_factory = file_factory
        self.file_serializer = file_serializer
        self.ai_call_repository = ai_call_repository
        self.ai_call_factory = ai_call_factory
        self.transpose_file_bill_to_models_use_case = transpose_file_bill_to_models_use_case

    def execute(
        self,
        uploaded_file: UploadedFile,
        user_id: int,
        model: str = LlmModels.DEEPSEEK_CHAT.name,
        user_provided_description: str = None,
    ):
        logger.info(f"[UploadSheet] Starting upload for user {user_id}, file: {uploaded_file.name}, model: {model}")

        file = self.file_factory.build(uploaded_file)
        saved_file = self.file_repository.create(file, user_id)
        logger.info(f"[UploadSheet] File saved with id: {saved_file.id}")

        logger.info(f"[UploadSheet] Extracting text from spreadsheet...")
        spreadsheet_text = saved_file.extract_text_from_spreadsheet()
        logger.info(f"[UploadSheet] Extracted {len(spreadsheet_text)} characters from spreadsheet")

        prompt = [SPREADSHEET_PROMPT]
        if user_provided_description:
            logger.info(f"[UploadSheet] User provided description: {user_provided_description[:100]}...")
            prompt.append(USER_PROVIDED_DESCRIPTION_PROMPT.format(user_provided_description=user_provided_description))
        prompt.append(f"Here is the spreadsheet content:\n{spreadsheet_text}")

        logger.info(f"[UploadSheet] Calling AI with model: {model}...")
        ai_call_id = self.ask_use_case.execute(prompt, response_format="json_object", model=model)
        logger.info(f"[UploadSheet] AI call completed with id: {ai_call_id}")

        ai_call = self.ai_call_repository.get(ai_call_id)
        saved_file.update_ai_info(ai_call)
        updated_file = self.file_repository.update(saved_file)
        logger.info(f"[UploadSheet] File updated with AI info")

        logger.info(f"[UploadSheet] Transposing file bills to models...")
        self.transpose_file_bill_to_models_use_case.execute(updated_file.id, user_id)
        logger.info(f"[UploadSheet] Upload completed successfully for file: {updated_file.id}")

        return self.file_serializer.serialize(updated_file)
