from modules.ai.domains.ai_call import AICallDomain


class AICallSerializer:
    def serialize(self, ai_call: AICallDomain) -> dict:
        prompt = "<omitido>"
        response = ai_call.response

        if ai_call.ai_message_content:
            response = ai_call.ai_message_content
            prompt = ai_call.user_message_content

        elif ai_call.related_to == "file":
            prompt = ai_call.file_url

        elif ai_call.related_to == "conversation":
            response = ai_call.conversation_title

        return {
            "id": ai_call.id,
            "created_at": ai_call.created_at,
            "updated_at": ai_call.updated_at,
            "prompt": prompt,
            "response": response,
            "total_tokens": ai_call.total_tokens,
            "input_used_tokens": ai_call.input_used_tokens,
            "output_used_tokens": ai_call.output_used_tokens,
            "model": ai_call.model,
            "is_error": ai_call.is_error,
            "model_prices": ai_call.model_prices(),
            "related_to": ai_call.related_to,
            "file_url": ai_call.file_url,
            "conversation_title": ai_call.conversation_title,
            "user_message_content": ai_call.user_message_content,
            "ai_message_content": ai_call.ai_message_content,
        }
