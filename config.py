import os
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()

def get_secret(key, default=None):
    """
    Safely retrieves secrets from Streamlit Cloud or local environment.
    Performs a lazy import of Streamlit so this module can be used
    in non-Streamlit contexts (CLI, tests, etc.).
    """
    try:
        import streamlit as st  # local import to avoid top-level dependency
        try:
            if key in st.secrets:
                return st.secrets[key]
        except (FileNotFoundError, RuntimeError, AttributeError):
            # Streamlit secrets not available or secrets file missing
            pass
    except ImportError:
        # Streamlit not installed in this environment; fall back to env vars
        pass

    return os.getenv(key, default)


class Config:
    """
    Configuration class for VERITAS.
    Uses safe retrieval to support both local and cloud environments.
    """
    APP_TITLE = "VERITAS"
    GROQ_API_KEY = get_secret("GROQ_API_KEY")
    TAVILY_API_KEY = get_secret("TAVILY_API_KEY")

    GROQ_BASE_URL = "https://api.groq.com/openai/v1"

    # Model configuration
    GROQ_MODEL = "llama-3.3-70b-versatile"
    MODEL_NAME = "llama-3.3-70b-versatile"

    LOG_LEVEL = "INFO"
    LOG_FILE = "veritas.log"
    MAX_CLAIMS_PER_TEXT = 20
    TAVILY_SEARCH_DEPTH = "advanced"
    TAVILY_MAX_RESULTS = 5
    APP_VERSION = "1.0.0"

    @staticmethod
    def validate_configuration():
        return bool(Config.GROQ_API_KEY and Config.TAVILY_API_KEY)

    # Backwards-compatible instance method expected by other modules
    def validate(self):
        return self.validate_configuration()


config = Config()
