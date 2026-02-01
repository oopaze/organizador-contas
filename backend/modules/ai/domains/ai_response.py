import random

from openai.types.chat import ChatCompletion


class AIResponseDomain:
    FALLBACK_ERROR_MESSAGES = [
        "Desculpa, viajei por um instante aqui. Pode repetir? ☁️",
        "Foi mal, entrei no mundo da lua agora. O que você disse? 🌙",
        "Oops, me distraí sonhando acordado. Pode repetir a pergunta? ✨",
        "Perdão, acabei me perdendo nos meus pensamentos. Pode repetir? 💭",
        "Desculpa, dei uma viajada agora e perdi o fio da meada. 🚀",
        "Tive um pequeno lapso de atenção aqui. Pode repetir a pergunta? 🫠",
        "Mal aí, me perdi nos pensamentos por um segundo. Repete para mim? ⏳",
        "Desculpa, meu cérebro foi dar uma volta no espaço. Pode repetir? 🪐",
        "Entrei no modo sonhador e acabei me distraindo. O que você perguntou? 🌌",
        "Ops, a conexão com a Terra falhou por um instante. Pode repetir? 📡"
    ]

    def __init__(
        self, 
        total_tokens: int = None,
        input_used_tokens: int = 0,
        output_used_tokens: int = 0,
        prompt: list[str] = None,
        response: dict = None,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        ai_response: ChatCompletion = None,
        model: str = None,
        is_error: bool = False,
    ):
        self.total_tokens = total_tokens
        self.input_used_tokens = input_used_tokens
        self.output_used_tokens = output_used_tokens
        self.prompt = prompt
        self.response = response
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.ai_response = ai_response
        self.model = model
        self.is_error = is_error

    @classmethod
    def get_fallback_error_message(cls):
        return random.choice(cls.FALLBACK_ERROR_MESSAGES)
