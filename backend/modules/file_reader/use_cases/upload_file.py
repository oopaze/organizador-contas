from django.db import transaction

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

### TAXONOMIA DE CATEGORIAS (Obrigatório para Transações):
Utilize EXATAMENTE as chaves abaixo para o campo category dentro da lista de transações. Escolha a mais específica possível.
- FOOD: food, food_grocery, food_restaurant, food_delivery
- HOUSING: housing, housing_rent, housing_condo, housing_maintenance
- BILL: bill, bill_water, bill_electricity, bill_gas, bill_internet, bill_phone
- TRANSPORT: transport, transport_fuel, transport_public, transport_apps, transport_maintenance
- HEALTH: health, health_pharmacy, health_appointments, health_exams, health_insurance
- EDUCATION: education, education_tuition, education_courses, education_books
- FINANCIAL: financial, credit_card, loans, taxes, insurance, subscriptions
- LIFESTYLE: lifestyle, leisure, travel, personal_shopping, gifts_donations
- INCOME: income, earnings, refunds
- OTHER: other

### REGRAS DE CATEGORIZAÇÃO:
1. Fatura (Nível Superior): O campo category principal para a fatura global deve ser SEMPRE credit_card. Não tente inferir outra categoria para o cabeçalho.
2. Transações (Subtransações): Analise o nome do estabelecimento (descrição) de cada item e atribua a categoria da taxonomia acima que seja mais provável.
  2.1 Ex: "Uber/99" -> transport_apps
  2.2 Ex: "iFood/Rappi" -> food_delivery
  2.3 Ex: "Farmácia/CVS/Droga Raia" -> health_pharmacy
  2.4 Ex: "Netflix/Spotify/Amazon Prime" -> subscriptions
3. Incerteza nas Transações: Se não houver uma subcategoria clara para o item, utilize a categoria pai (ex: utilize food se não conseguir distinguir entre supermercado ou restaurante).

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
   - IGNORE: Pagamentos da fatura anterior, Juros de atraso listados no rodapé, limites e saldo total parcelado.
   
   ⚠️ REGRA DE PARCELAMENTO (installment_info):
   - Formato Obrigatório: "X/Y" (Atual/Total).
   - Limpeza: Remova palavras como "Parcela", "Parc.", "de", "of" e zeros à esquerda.
   - Exemplo Input: "Parcela 01 de 10"  -> Output: "1/10"
   - Exemplo Input: "Parc. 05/12"       -> Output: "5/12"
   - Exemplo Input: (Sem parcelamento)  -> Output: null

### FORMATO DE RESPOSTA (JSON APENAS):
{{
  "bill_identifier": "string",
  "total_amount": 150.00,
  "due_date": "YYYY-MM-DD",
  "transaction_type": "incoming",
  "category": "credit_card",
  "transactions": [
    {{
      "date": "YYYY-MM-DD",
      "description": "string",
      "amount": 50.00,
      "installment_info": "1/6",
      "category": "string"
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

    @transaction.atomic
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
            self.remove_pdf_password_use_case.execute(saved_file, password)

        # Extract text from PDF - works with both local and S3 storage
        pdf_text = saved_file.extract_text_from_pdf(password)

        prompt = [PROMPT, f"Here is the PDF content: name: {file.name}, text: {pdf_text}"]
        ai_call_id = self.ask_use_case.execute(prompt, user_id, response_format="json_object", model=model)

        ai_call = self.ai_call_repository.get(ai_call_id)
        saved_file.update_ai_info(ai_call)
        updated_file = self.file_repository.update(saved_file)

        transaction_ids = self.transpose_file_bill_to_models_use_case.execute(updated_file.id, user_id, create_in_future_months)
        serialized_file = self.file_serializer.serialize(updated_file)
        return {**serialized_file, "transaction_ids": transaction_ids}
