from modules.ai.chat.domains import AICallDomain


class AICallSerializer:
    def serialize(self, ai_call: "AICallDomain") -> dict:
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
    
    def serialize_without_prompt_and_response(self, ai_call: "AICallDomain") -> dict:
        return {
            "id": ai_call.id,
            "created_at": ai_call.created_at,
            "updated_at": ai_call.updated_at,
            "total_tokens": ai_call.total_tokens,
            "input_used_tokens": ai_call.input_used_tokens,
            "output_used_tokens": ai_call.output_used_tokens,
        }
