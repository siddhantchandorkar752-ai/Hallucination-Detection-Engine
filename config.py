import os
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

class Config:
    """
    Configuration class for VERITAS Hallucination Detection Engine.
    Prioritizes Streamlit Secrets for cloud deployment and fallbacks to os.getenv for local dev.
    """
    # API Keys integration
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY") or os.getenv("TAVILY_API_KEY")
    
    # API Endpoints
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    
    # Model configuration (Using both names to prevent AttributeErrors in app.py and verifier.py)
    GROQ_MODEL = "llama-3.3-70b-versatile"
    MODEL_NAME = "llama-3.3-70b-versatile"
    
    # Logging and Processing limits
    LOG_LEVEL = "INFO"
    LOG_FILE = "veritas.log"
    MAX_CLAIMS_PER_TEXT = 10
    
    # Search Engine Configuration
    TAVILY_SEARCH_DEPTH = "advanced"
    TAVILY_MAX_RESULTS = 5
    APP_VERSION = "1.0.0"

    @staticmethod
    def validate_configuration():
        """Validates that mandatory API keys are present."""
        if not Config.GROQ_API_KEY or not Config.TAVILY_API_KEY:
            return False
        return True

config = Config()
