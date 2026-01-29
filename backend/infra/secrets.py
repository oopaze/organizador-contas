from os import environ
from dotenv import load_dotenv

load_dotenv()

GOOGLE_AI_API_KEY = environ.get("GOOGLE_AI_API_KEY", "google-ai-key")
OPENAI_API_KEY = environ.get("OPENAI_API_KEY", "openai-key")

# Database
DATABASE_NAME = environ.get("DATABASE_NAME", "bills_manager")
DATABASE_USER = environ.get("DATABASE_USER", "postgres")
DATABASE_PASSWORD = environ.get("DATABASE_PASSWORD", "postgres")
DATABASE_HOST = environ.get("DATABASE_HOST", "localhost")
DATABASE_PORT = environ.get("DATABASE_PORT", "5432")
