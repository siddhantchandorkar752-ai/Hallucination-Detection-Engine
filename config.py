import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "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")
    GROQ_MODEL = "llama-3.3-70b-versatile"
    LOG_LEVEL = "INFO"
    LOG_FILE = "veritas.log"
    MAX_CLAIMS_PER_TEXT = 20
    TAVILY_SEARCH_DEPTH = "advanced"
    TAVILY_MAX_RESULTS = 5
    CONFIDENCE_THRESHOLD = 0.75
    MODES = ["General", "Medical", "Legal", "Scientific"]
    APP_VERSION = "3.0.0"

config = Config()
