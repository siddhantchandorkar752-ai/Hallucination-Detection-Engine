import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    GROQ_MODEL = "llama-3.3-70b-versatile"
    MODEL_NAME = "llama-3.3-70b-versatile"
    LOG_LEVEL = "INFO"
    LOG_FILE = "veritas.log"
    MAX_CLAIMS_PER_TEXT = 10
    TAVILY_SEARCH_DEPTH = "advanced"
    TAVILY_MAX_RESULTS = 5
    APP_VERSION = "1.0.0"

config = Config()
