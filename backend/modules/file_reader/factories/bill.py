from modules.file_reader.domains.bill import BillDomain
from modules.file_reader.domains.file import FileDomain
from modules.file_reader.factories.file import FileFactory
from modules.transactions.models import Transaction

# Month name to number mapping (Portuguese)
MONTH_MAP = {
    'janeiro': '01', 'fevereiro': '02', 'março': '03', 'marco': '03',
    'abril': '04', 'maio': '05', 'junho': '06',
    'julho': '07', 'agosto': '08', 'setembro': '09',
    'outubro': '10', 'novembro': '11', 'dezembro': '12',
}


class BillFactory:
    def __init__(self, file_factory: FileFactory):
        self.file_factory = file_factory

    def _get_due_date_from_monthly_format(self, ai_response: dict) -> str | None:
        """Extract due_date from monthly format (ano/mes)."""
        ano = ai_response.get("ano")
        mes = ai_response.get("mes")

        if ano and mes:
            # Convert month name to number
            if isinstance(mes, str):
                mes_lower = mes.lower()
                mes_num = MONTH_MAP.get(mes_lower, "01")
            else:
                mes_num = str(mes).zfill(2)

            # Use first day of month as due_date
            return f"{ano}-{mes_num}-01"
        return None

    def build_from_file(self, file: FileDomain, ai_response: dict = None) -> BillDomain:
        if ai_response is None:
            ai_response = file.ai_call.response

        # Determine transaction_type based on is_income flag
        is_income = ai_response.get("is_income", False)
        transaction_type = "incoming" if is_income else "outgoing"

        # Handle different field names that AI might return
        due_date = (
            ai_response.get("due_date") or
            ai_response.get("date") or
            ai_response.get("data") or
            self._get_due_date_from_monthly_format(ai_response)
        )
        total_amount = (
            ai_response.get("total_amount") or
            ai_response.get("amount") or
            ai_response.get("valor") or
            ai_response.get("valor_meu") or
            ai_response.get("valor_total") or
            0
        )
        bill_identifier = (
            ai_response.get("bill_identifier") or
            ai_response.get("description") or
            ai_response.get("descricao") or
            ai_response.get("nome") or
            ai_response.get("item") or
            "Unknown"
        )

        if not due_date:
            raise ValueError(f"Missing due_date in AI response: {ai_response}")

        return BillDomain(
            due_date=due_date,
            total_amount=total_amount,
            bill_identifier=bill_identifier,
            file=file,
            transaction_type=transaction_type,
        )

    def build_from_model(self, model: Transaction) -> BillDomain:
        return BillDomain(
            due_date=model.due_date,
            total_amount=model.total_amount,
            bill_identifier=model.transaction_identifier,
            file=self.file_factory.build_from_model(model.file),
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
