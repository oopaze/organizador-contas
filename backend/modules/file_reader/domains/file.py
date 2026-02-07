import re
import csv
import io

from pdfplumber import open as pdf_open
import pandas as pd

from modules.file_reader.domains.ai_call import AICallDomain

NOISE_PATTERNS = [
    r'central de atendimento',
    r'ouvidoria',
    r'sac',
    r'juros.*%|cet',
    r'instruções|como pagar',
    r'código de barras',
    r'pagável preferencialmente',
    r'baixe o app',
    r'deficiência auditiva',
    r'\b\d{5}-\d{3}\b',  # CEP
]

SUMMARY_PATTERNS = [
    r'^compras\b',
    r'^parcelamentos\b',
    r'^valores recebidos\b',
    r'^fatura anterior\b',
]


class FileDomain:
    def __init__(
        self,
        url: str = None,
        uploaded_file: str = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        raw_text: str = None,
        ai_call: AICallDomain = None,
        user_id: int = None,
    ):
        self.url = self._format_url(url)
        self.uploaded_file = uploaded_file
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.raw_text = raw_text
        self.ai_call = ai_call
        self.user_id = user_id

    def get_response(self) -> dict | list[dict]:
        return self.ai_call.response if self.ai_call else None

    def update_ai_info(self, ai_call: AICallDomain):
        self.ai_call = ai_call

    def _format_url(self, url: str):
        if not url:
            return
        return f".{url}"

    def is_saved(self):
        return self.url != ""

    @property
    def file(self):
        return self.url or self.uploaded_file
    
    def extract_text_from_pdf(self, password: str = None):
        """
        Extract text from PDF file.
        Works with both local filesystem and S3 storage.
        """
        if not self.is_saved():
            raise Exception("File is not saved")

        # Open the file - works with both local path and S3 file object
        # The uploaded_file is a FieldFile that can be opened directly
        with self.uploaded_file.open('rb') as file_obj:
            with pdf_open(file_obj, password=password) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()

        self.raw_text = self._clean_text(text)
        self.raw_text = self._keep_financial_lines(self.raw_text)
        self.raw_text = self._remove_summary_lines(self.raw_text)
        self.raw_text = "".join(self.raw_text)
        return self.raw_text
    
    def _keep_financial_lines(self, text: str) -> str:
        lines = text.splitlines()
        kept = []

        for line in lines:
            if (
                "R$" in line
                or re.search(r'\d{2}/\d{2}', line)  # datas
                or any(k in line.lower() for k in [
                    "total", "vencimento", "pagamento", "fatura", "resumo", "fatura anterior"
                ])
            ):
                kept.append(line)

        return "\n".join(kept)

    def _clean_text(self, text: str):
        lines = text.splitlines()
        clean_lines = []

        for line in lines:
            l = line.lower().strip()

            if not l:
                continue

            if any(re.search(p, l) for p in NOISE_PATTERNS):
                continue

            clean_lines.append(line)
        return "\n".join(clean_lines)

    def _remove_summary_lines(self, lines):
        result = []
        for line in lines:
            l = line.lower().strip()
            if any(re.search(p, l) for p in SUMMARY_PATTERNS):
                continue
            result.append(line)
        return result

    def extract_text_from_spreadsheet(self) -> str:
        """
        Extract text from CSV or Excel files and return as formatted string.
        For Excel files, reads all sheets and combines them.
        Works with both local filesystem and S3 storage.
        """
        if not self.is_saved():
            raise Exception("File is not saved")

        # Get file extension from the uploaded_file name
        file_name = self.uploaded_file.name
        file_extension = file_name.lower().split('.')[-1]

        try:
            # Open file - works with both local and S3 storage
            with self.uploaded_file.open('rb') as file_obj:
                if file_extension == 'csv':
                    df = pd.read_csv(file_obj)
                    self.raw_text = df.to_csv(index=False)
                elif file_extension in ['xlsx', 'xls']:
                    # Read all sheets from Excel file
                    excel_file = pd.ExcelFile(file_obj)
                    all_sheets_text = []

                    for sheet_name in excel_file.sheet_names:
                        df = pd.read_excel(excel_file, sheet_name=sheet_name)
                        if not df.empty:
                            sheet_text = f"=== Sheet: {sheet_name} ===\n{df.to_csv(index=False)}"
                            all_sheets_text.append(sheet_text)

                    self.raw_text = "\n\n".join(all_sheets_text)
                else:
                    raise Exception(f"Unsupported file format: {file_extension}")

            return self.raw_text
        except Exception as e:
            raise Exception(f"Error reading spreadsheet: {str(e)}")
