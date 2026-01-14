import re

from pdfplumber import open as pdf_open

from modules.pdf_reader.domains.ai_call import AICallDomain

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
    ):
        self.url = self._format_url(url)
        self.uploaded_file = uploaded_file
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.raw_text = raw_text
        self.ai_call = ai_call

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
    
    def extract_text_from_pdf(self):
        if not self.is_saved():
            raise Exception("File is not saved")
        
        with pdf_open(self.url) as pdf:
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
