
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
Aja como um extrator de dados financeiros de alta precisão. 
Você receberá o NOME do arquivo e o TEXTO de uma fatura de cartão de crédito.

### DADOS RECEBIDOS:
- FILE NAME: {file_name}
- PDF TEXT: {pdf_text}

### ⚖️ REGRA CRÍTICA DE SINAIS E NATUREZA (STRICT):
No meu sistema, a lógica de sinais é mandatória:
- DESPESAS (Saídas/Gastos): Devem ser SEMPRE números POSITIVOS (ex: 150.00).
- RECEITAS/DESCONTOS (Entradas/Estornos): Devem ser SEMPRE números NEGATIVOS (ex: -50.00).

Como faturas de cartão são majoritariamente compostas por gastos:
1. Extraia compras e lançamentos de débito como valores POSITIVOS.
2. Extraia estornos, créditos de recompensa ou ajustes a seu favor como valores NEGATIVOS.
3. 'transaction_type' da fatura (bill) deve ser "incoming", pois ela representa um boleto a ser pago.

### REGRAS DE IDENTIFICAÇÃO (bill_identifier):
- Use o nome da Instituição Financeira no TEXTO.
- Fallback: Use o FILE NAME (limpando extensões e prefixos como "fatura_").
- Se não identificar, retorne "UNKNOWN_BANK".

### REGRAS DE EXTRAÇÃO:
1. INFORMAÇÕES BÁSICAS: bill_identifier, total_amount (positivo), due_date (YYYY-MM-DD).
2. TRANSAÇÕES: Extraia date, description, amount (seguindo a regra de sinais acima) e installment_info.
- IGNORE: Pagamentos de fatura anterior, limites e ofertas.

### FORMATO DE RESPOSTA (JSON APENAS):
{{
  "bill_identifier": "string",
  "total_amount": 150.00,
  "due_date": "YYYY-MM-DD",
  "transaction_type": "incoming",
  "transactions": [
    {{
      "date": "YYYY-MM-DD",
      "description": "string",
      "amount": 50.00,
      "installment_info": "string"
    }}
  ]
}}
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

        prompt = [PROMPT, f"Here is the PDF content: name: {file.name}, text: {pdf_text}"]
        ai_call_id = self.ask_use_case.execute(prompt, response_format="json_object", model=model)

        ai_call = self.ai_call_repository.get(ai_call_id)
        saved_file.update_ai_info(ai_call)
        updated_file = self.file_repository.update(saved_file)

        self.transpose_file_bill_to_models_use_case.execute(updated_file.id, user_id, create_in_future_months)
        return self.file_serializer.serialize(updated_file)
