import io
import PyPDF2
from django.core.files.base import ContentFile

from modules.file_reader.domains.file import FileDomain
from modules.file_reader.exceptions import InvalidPasswordException

class RemovePDFPasswordUseCase:
    def execute(self, file: FileDomain, password: str):
        """
        Remove password from PDF file.
        Works with both local filesystem and S3 storage.
        """
        # Read the file content - works with both local and S3
        with file.uploaded_file.open('rb') as file_obj:
            file_content = file_obj.read()

        # Create a BytesIO object from the content
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        if not pdf_reader.is_encrypted:
            return  # No password to remove

        try:
            result = pdf_reader.decrypt(password)
            if result == 0:
                raise InvalidPasswordException("Senha inválida para o PDF")
        except Exception as e:
            if "Invalid password" in str(e) or "Senha inválida" in str(e):
                raise
            raise InvalidPasswordException("Senha inválida para o PDF")

        # Create new PDF without password
        pdf_writer = PyPDF2.PdfWriter()
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        # Write to BytesIO
        output_buffer = io.BytesIO()
        pdf_writer.write(output_buffer)
        output_buffer.seek(0)

        # Save back to the same file (works with both local and S3)
        file.uploaded_file.save(
            file.uploaded_file.name,
            ContentFile(output_buffer.read()),
            save=True
        )
