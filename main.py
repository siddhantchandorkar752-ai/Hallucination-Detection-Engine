from config import config
from logger import logger

def main():
    logger.info(f"Starting {config.APP_TITLE} v{config.APP_VERSION}")
    config.validate()
    logger.info("API keys validated successfully.")
    logger.info("Run: streamlit run app.py")

if __name__ == "__main__":
    main()
