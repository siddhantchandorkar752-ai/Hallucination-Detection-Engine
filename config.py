import os

class Config:
    GROQ_API_KEY = "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"
    TAVILY_API_KEY = "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"
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    GROQ_MODEL = "llama-3.3-70b-versatile"
    MODEL_NAME = "llama-3.3-70b-versatile"
    LOG_LEVEL = "INFO"
    LOG_FILE = "veritas.log"
    MAX_CLAIMS_PER_TEXT = 10
    TAVILY_SEARCH_DEPTH = "advanced"
    TAVILY_MAX_RESULTS = 5
    APP_VERSION = "1.0.0"

    @staticmethod
    def validate():
        if not Config.GROQ_API_KEY.startswith("gsk_"):
            raise ValueError("Invalid GROQ API Key format")
        if not Config.TAVILY_API_KEY.startswith("tvly-"):
            raise ValueError("Invalid TAVILY API Key format")

config = Config()
