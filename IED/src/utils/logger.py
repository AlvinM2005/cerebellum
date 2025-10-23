# ./src/utils/logger.py
import logging
from utils.config import LOGS_DIR
from datetime import datetime

def get_logger(name: str = "nback") -> logging.Logger:
    """
    Get a logger with both file and console output.

    Args:
        name (str): Logger name (recommended: module name)

    Returns:
        logging.Logger: Configured logger instance
    """
    # Ensure the log directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Log file name
    log_filename = LOGS_DIR / f"nback.log"

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Record all levels by default

    # Avoid adding duplicate handlers
    if not logger.handlers:
        # File handler (write to file)
        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        # Console handler (output to terminal)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
