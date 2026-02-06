from modules.base.types import TypeItem, BaseType


class LlmProviders(BaseType):
    GOOGLE = TypeItem("google")
    DEEPSEEK = TypeItem("deepseek")
    OPENAI = TypeItem("openai")


class LlmModels(BaseType):
    default_kwargs = {
        "temperature_enabled": True,
    }

    # Google Models
    GOOGLE_GEMINI_2_5_FLASH_LITE = TypeItem(
        "gemini-2.5-flash-lite", 
        provider=LlmProviders.GOOGLE.name,
        input_cost_per_million_tokens=0.1,
        output_cost_per_million_tokens=0.4,
        default=default_kwargs
    )
    GOOGLE_GEMINI_2_5_FLASH = TypeItem(
        "gemini-2.5-flash", 
        provider=LlmProviders.GOOGLE.name,
        input_cost_per_million_tokens=0.3,
        output_cost_per_million_tokens=2.5,
        default=default_kwargs
    )
    GOOGLE_GEMINI_2_5_PRO = TypeItem(
        "gemini-2.5-pro", 
        provider=LlmProviders.GOOGLE.name, 
        input_cost_per_million_tokens=1.25,
        output_cost_per_million_tokens=10,
        default=default_kwargs
    )
    GOOGLE_GEMINI_3_FLASH_PREVIEW = TypeItem(
        "gemini-3-flash-preview", 
        provider=LlmProviders.GOOGLE.name,
        input_cost_per_million_tokens=0.5,
        output_cost_per_million_tokens=3,
        default=default_kwargs
    )
    GOOGLE_GEMINI_3_PRO_PREVIEW = TypeItem(
        "gemini-3-pro-preview", 
        provider=LlmProviders.GOOGLE.name,
        input_cost_per_million_tokens=2,
        output_cost_per_million_tokens=12,
        default=default_kwargs
    )

    # DeepSeek Models
    DEEPSEEK_CHAT = TypeItem(
        "deepseek-chat", 
        provider=LlmProviders.DEEPSEEK.name,
        input_cost_per_million_tokens=0.27,
        output_cost_per_million_tokens=0.42,
        default=default_kwargs
    )
    DEEPSEEK_REASONER = TypeItem(
        "deepseek-reasoner", 
        provider=LlmProviders.DEEPSEEK.name,
        input_cost_per_million_tokens=0.27,
        output_cost_per_million_tokens=0.42,
        default=default_kwargs
    )

    # OpenAI Models
    CHAT_GPT_5_NANO = TypeItem(
        "gpt-5-nano", 
        provider=LlmProviders.OPENAI.name,
        input_cost_per_million_tokens=0.05,
        output_cost_per_million_tokens=0.4,
        default=default_kwargs,
        temperature_enabled=False
    )
    CHAT_GPT_5_MINI = TypeItem(
        "gpt-5-mini", 
        provider=LlmProviders.OPENAI.name,
        input_cost_per_million_tokens=0.25,
        output_cost_per_million_tokens=2,
        default=default_kwargs,
        temperature_enabled=False
    )
    CHAT_GPT_5 = TypeItem(
        "gpt-5", 
        provider=LlmProviders.OPENAI.name,
        input_cost_per_million_tokens=1.25,
        output_cost_per_million_tokens=10,
        default=default_kwargs,
        temperature_enabled=False
    )
    EMBEDDING_GPT_5 = TypeItem(
        "text-embedding-3-small", 
        provider=LlmProviders.OPENAI.name,
        input_cost_per_million_tokens=0.02,
        output_cost_per_million_tokens=0,
        default=default_kwargs,
        temperature_enabled=False
    )

    @classmethod
    def get_model(cls, name: str) -> TypeItem:
        return cls.get_by_name(name)

    @classmethod
    def get_provider(cls, name: str) -> str:
        return cls.get_by_name(name).provider
