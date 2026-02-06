from modules.ai.domains.ai_call import AICallDomain
from modules.ai.models import AICall


class AICallFactory:
    def build_from_model(self, model: AICall) -> AICallDomain:
        return AICallDomain(
            prompt=model.prompt,
            response=model.response,
            total_tokens=model.total_tokens,
            input_used_tokens=model.input_used_tokens,
            output_used_tokens=model.output_used_tokens,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            model=model.model,
            is_error=model.is_error,
            related_to=getattr(model, "related_to", None),
            file_url=model.files.first().raw_file.url if model.files.first() else None,
            conversation_title=model.conversations.first().title if model.conversations.first() else None,
            user_message_content=model.messages.first().content if model.messages.first() else None,
            ai_message_content=model.messages.last().content if model.messages.last() else None,
        )
