from modules.file_reader.domains.file import FileDomain
from modules.file_reader.serializers.ai_call import AICallSerializer


class FileSerializer:
    def __init__(self, ai_call_serializer: AICallSerializer):
        self.ai_call_serializer = ai_call_serializer

    def serialize(self, file: FileDomain) -> dict:
        return {
            "id": file.id,
            "url": file.url,
            "created_at": file.created_at,
            "updated_at": file.updated_at,
            "raw_text": file.raw_text,
            "ai_call": self.ai_call_serializer.serialize(file.ai_call),
        }
