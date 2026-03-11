import logging
import sys


def setup_logging(debug: bool = False):
    format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_handler.setFormatter(logging.Formatter(format))

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO, handlers=[console_handler]
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
