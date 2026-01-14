from os import environ
from dotenv import load_dotenv 

load_dotenv()

GOOGLE_AI_API_KEY = environ.get("GOOGLE_AI_API_KEY", "google-ai-key")
