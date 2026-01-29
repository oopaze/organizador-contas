from modules.file_reader.domains.ai_call import AICallDomain


class AICallSerializer:
    def serialize(self, ai_call: AICallDomain) -> dict:
        return {
            "id": ai_call.id,
            "created_at": ai_call.created_at,
            "updated_at": ai_call.updated_at,
            "prompt": ai_call.prompt,
            "response": ai_call.response,
            "total_tokens": ai_call.total_tokens,
            "input_used_tokens": ai_call.input_used_tokens,
            "output_used_tokens": ai_call.output_used_tokens,
        }
