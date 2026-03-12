import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TEMPERATURE: float = 0.1
    GROQ_MAX_TOKENS: int = 2048
    TAVILY_MAX_RESULTS: int = 5
    TAVILY_SEARCH_DEPTH: str = "advanced"
    MAX_CLAIMS_PER_TEXT: int = 10
    CONFIDENCE_THRESHOLD: float = 0.7
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "veritas.log"
    APP_TITLE: str = "Veritas â€” LLM Hallucination Detection Engine"
    APP_VERSION: str = "1.0.0"

    @classmethod
    def validate(cls):
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY missing in .env")
        if not cls.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY missing in .env")

config = Config()
