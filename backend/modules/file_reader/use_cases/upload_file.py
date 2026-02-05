
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

### 🛡️ TRATAMENTO DE ARMADILHAS VISUAIS (CRÍTICO):
Faturas bancárias (especialmente Banco Inter e Nubank) usam hifens como separadores visuais.
- PADRÃO VISUAL: "Loja Exemplo - R$ 50,00" -> O hífen aqui é apenas estética. NÃO é um número negativo.
- AÇÃO: Ignore hifens que aparecem entre a descrição e o símbolo da moeda.

### ⚖️ REGRA DE SINAIS E NATUREZA:
1. COMPRAS E GASTOS (Padrão):
   - Devem ser SEMPRE números POSITIVOS (ex: 150.00).
   - Assuma que QUALQUER transação é uma despesa (positiva) a menos que contenha palavras-chave explícitas de estorno.

2. RECEITAS E ESTORNOS (Exceção):
   - Devem ser SEMPRE números NEGATIVOS (ex: -50.00).
   - Aplique negativo APENAS se a descrição contiver: "Estorno", "Crédito", "Cancelamento", "Devolução" ou "Pagamento Antecipado".

3. TIPO DE TRANSAÇÃO:
   - 'transaction_type' da fatura (bill) deve ser "incoming" (boleto a pagar).

### REGRAS DE IDENTIFICAÇÃO (bill_identifier):
- Use o nome da Instituição Financeira no TEXTO (Ex: Banco Inter, Nubank, C&A Pay).
- Fallback: Use o FILE NAME (limpando extensões).
- Se não identificar, retorne "UNKNOWN_BANK".

### REGRAS DE EXTRAÇÃO:
1. INFORMAÇÕES BÁSICAS: bill_identifier, total_amount (positivo), due_date (YYYY-MM-DD).
2. TRANSAÇÕES: Extraia date, description, amount e installment_info.
   - Dica de Valor: Se o texto for "NETFLIX - R$ 55,90", o valor é 55.90 (Positivo).
   - Dica de Valor: Se o texto for "Estorno Uber - R$ 10,00", o valor é -10.00 (Negativo).
   - IGNORE: Pagamentos da fatura anterior, Juros de atraso listados no rodapé, limites e saldo total parcelado (pegue apenas as parcelas do mês).

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
