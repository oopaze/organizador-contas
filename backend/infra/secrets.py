from os import environ
from dotenv import load_dotenv

load_dotenv()

# AI
GOOGLE_AI_API_KEY = environ.get("GOOGLE_AI_API_KEY", "google-ai-key")
GOOGLE_AI_BASE_URL = environ.get("GOOGLE_AI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")

OPENAI_API_KEY = environ.get("OPENAI_API_KEY", "openai-key")
OPENAI_BASE_URL = environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

DEEPSEEK_API_KEY = environ.get("DEEPSEEK_API_KEY", "deepseek-key")
DEEPSEEK_BASE_URL = environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.ai")

# Database
DATABASE_NAME = environ.get("DATABASE_NAME", "bills_manager")
DATABASE_USER = environ.get("DATABASE_USER", "postgres")
DATABASE_PASSWORD = environ.get("DATABASE_PASSWORD", "postgres")
DATABASE_HOST = environ.get("DATABASE_HOST", "localhost")
DATABASE_PORT = environ.get("DATABASE_PORT", "5432")
