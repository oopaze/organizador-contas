import os
import PyPDF2

from modules.file_reader.domains.file import FileDomain

class RemovePDFPasswordUseCase:
    def execute(self, file: FileDomain, password: str):
        path = file.uploaded_file.path
        with open(path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            if not pdf_reader.is_encrypted:
                return path
            
            try:
                pdf_reader.decrypt(password)
            except:
                raise Exception("Invalid password")

            pdf_writer = PyPDF2.PdfWriter()
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

            os.remove(path)
            with open(path, "wb") as output_file:
                pdf_writer.write(output_file)

        return path
