from django.core.files.uploadedfile import UploadedFile

from modules.file_reader.domains.ai_call import AICallDomain
from modules.file_reader.domains.file import FileDomain
from modules.file_reader.factories.ai_call import AICallFactory
from modules.file_reader.models import File


class FileFactory:
    def __init__(self, ai_call_factory: AICallFactory):
        self.ai_call_factory = ai_call_factory

    def build(self, file: UploadedFile) -> FileDomain:
        return FileDomain(uploaded_file=file)

    def build_from_model(self, model: File) -> FileDomain:
        url = model.raw_file.url if model.raw_file else ""
        return FileDomain(
            url=url,
            uploaded_file=model.raw_file,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            raw_text=model.raw_text,
            ai_call=self.ai_call_factory.build_from_model(model.ai_call) if model.ai_call else None,
        )
