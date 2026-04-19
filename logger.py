import logging
import os

def setup_logger():
    logger = logging.getLogger("VERITAS")
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    try:
        file_handler = logging.FileHandler("veritas.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        pass
    
    return logger

logger = setup_logger()
