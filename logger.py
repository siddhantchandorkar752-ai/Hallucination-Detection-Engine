import logging

def setup_logger():
    logger = logging.getLogger("VERITAS")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    try:
        fh = logging.FileHandler("veritas.log")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        pass
    return logger

logger = setup_logger()
