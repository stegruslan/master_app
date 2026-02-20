import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_logging():
    format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(format))

    file_handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(format))

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[console_handler, file_handler]
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)