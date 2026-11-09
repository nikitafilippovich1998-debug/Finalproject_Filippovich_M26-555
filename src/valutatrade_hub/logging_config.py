import logging
import os


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("valutatrade")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        fh = logging.FileHandler("logs/actions.log", encoding="utf-8")
        formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger

logger = setup_logging()