import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Ab ye keys system secrets se uthayega
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    MODEL_NAME = "llama-3.3-70b-versatile"
    LOG_LEVEL = "INFO" 
    APP_VERSION = "1.0.0"

    @staticmethod
    def validate():
        if not Config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY missing!")
        if not Config.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY missing!")

config = Config()
