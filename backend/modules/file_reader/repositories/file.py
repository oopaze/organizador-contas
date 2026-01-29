from modules.file_reader.domains.file import FileDomain
from modules.file_reader.factories.file import FileFactory
from modules.file_reader.models import File


class FileRepository:
    def __init__(self, model: File, file_factory: FileFactory):
        self.model = model
        self.file_factory = file_factory

    def get(self, file_id: str) -> FileDomain:
        file_instance = self.model.objects.get(id=file_id)
        return self.file_factory.build_from_model(file_instance)

    def create(self, file: FileDomain) -> FileDomain:
        file_instance = self.model.objects.create(raw_file=file.uploaded_file)
        return self.file_factory.build_from_model(file_instance)

    def update(self, file: FileDomain) -> FileDomain:
        file_instance = self.model.objects.get(id=file.id)

        if file.ai_call:
            file_instance.ai_call_id = file.ai_call.id
        
        file_instance.raw_text = file.raw_text
        file_instance.save()
        return self.file_factory.build_from_model(file_instance)
