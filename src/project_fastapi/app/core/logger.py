import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent

LOG_DIR = APP_DIR / "logs" 
LOG_DIR.mkdir(exist_ok=True)

LOG_FORMAT = "[%(asctime)s] - [%(levelname)s] - [%(name)s] - [%(filename)s] - [%(message)s]"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger():
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    
    if logger.hasHandlers():
        logger.handlers.clear()
        
    fommater = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(fommater)
    logger.addHandler(console_handler)
    
    file_handler = RotatingFileHandler(
        filename= LOG_DIR/"app.log",
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(fommater)
    logger.addHandler(file_handler)
    
    return logger
    

logger = setup_logger()